import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from search_web import canonical_url, load_config, require_key

class SearchTests(unittest.TestCase):
  def test_canonical_url_removes_tracking_and_fragment(self):
    self.assertEqual(canonical_url("HTTPS://Example.COM/a/?utm_source=x#part"), "https://example.com/a/")

  def test_env_overrides_file(self):
    with tempfile.TemporaryDirectory() as d:
      p = Path(d) / "config.toml"
      p.write_text('serper_api_key = "file-key-123"\ndeepseek_api_key = "file-key-456"\n', encoding="utf-8")
      old = os.environ.get("SERPER_API_KEY")
      os.environ["SERPER_API_KEY"] = "env-key-123"
      try:
        cfg = load_config(p)
      finally:
        if old is None: os.environ.pop("SERPER_API_KEY", None)
        else: os.environ["SERPER_API_KEY"] = old
      self.assertEqual(cfg["serper_api_key"], "env-key-123")
      self.assertEqual(cfg["deepseek_api_key"], "file-key-456")

  def test_short_key_rejected(self):
    with self.assertRaises(RuntimeError): require_key("TEST", "short")

if __name__ == "__main__": unittest.main()
