import json
import os
import tempfile
import unittest
from unittest.mock import patch

from core.comfyui_video_engine import ComfyUIVideoEngine, VideoGenerationError
from ai.groq_director import GroqCreativeDirector, CreativeDirectorError


class ComfyUIVideoEngineTests(unittest.TestCase):
    def test_video_file_discovery_supports_common_comfyui_output_keys(self):
        outputs = {
            "10": {"images": [{"filename": "preview.png"}]},
            "11": {"gifs": [{"filename": "final.mp4", "type": "output"}]},
            "12": {"videos": [{"filename": "clip.webm"}]},
            "13": {"files": [{"filename": "notes.txt"}]},
        }
        found = ComfyUIVideoEngine._video_files(outputs)
        self.assertEqual([item["filename"] for item in found], ["final.mp4", "clip.webm"])

    def test_prompt_input_is_updated_without_mutating_other_inputs(self):
        workflow = {"6": {"inputs": {"text": "old", "clip": ["1", 0]}}}
        ComfyUIVideoEngine._set_node_input(workflow, "6", "text", "new shot", "Positive prompt")
        self.assertEqual(workflow["6"]["inputs"]["text"], "new shot")
        self.assertEqual(workflow["6"]["inputs"]["clip"], ["1", 0])

    def test_missing_node_reports_actionable_error(self):
        with self.assertRaisesRegex(VideoGenerationError, "does not exist"):
            ComfyUIVideoEngine._set_node_input({}, "999", "text", "prompt", "Positive prompt")

    def test_optional_node_mapping_is_noop_when_not_configured(self):
        workflow = {"6": {"inputs": {"text": "unchanged"}}}
        ComfyUIVideoEngine._set_node_input(workflow, "", "text", 24, "Frame rate")
        self.assertEqual(workflow["6"]["inputs"]["text"], "unchanged")

    def test_load_workflow_reads_api_format_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "workflow.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"6": {"inputs": {"text": "prompt"}}}, handle)
            with patch.dict(os.environ, {
                "COMFYUI_WORKFLOW_PATH": path,
                "COMFYUI_PROMPT_NODE_ID": "6",
                "COMFYUI_BASE_URL": "http://127.0.0.1:8188",
            }, clear=False):
                engine = ComfyUIVideoEngine()
                self.assertIn("6", engine._load_workflow())


class CreativeDirectorTests(unittest.TestCase):
    def test_missing_api_key_fails_instead_of_returning_a_template(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=False):
            director = GroqCreativeDirector(api_key="")
            with self.assertRaisesRegex(CreativeDirectorError, "GROQ_API_KEY"):
                director.generate_storyboard("A cinematic film", target_duration=10)

    def test_example_placeholder_is_not_treated_as_a_real_api_key(self):
        director = GroqCreativeDirector(api_key="your_groq_api_key_here")
        self.assertFalse(director.api_key)


if __name__ == "__main__":
    unittest.main()
