import unittest
from unittest.mock import patch, MagicMock
from windsurf.scripts.generate_upload import main
from windsurf.scripts.pick_keyword import generate_keyword
from windsurf.scripts.dk_upload import upload


class TestMusicGeneration(unittest.TestCase):
    @patch('windsurf.scripts.pick_keyword.generate_keyword')
    @patch('windsurf.scripts.dk_upload.upload')
    def test_main_flow(self, mock_upload, mock_generate_keyword):
        # モックのキーワードを設定
        mock_generate_keyword.return_value = "テストキーワード"
        
        # モックのアップロード関数を設定
        mock_upload.return_value = None
        
        # メイン関数を実行
        main()
        
        # アサーション
        mock_generate_keyword.assert_called_once()
        mock_upload.assert_called_once()

    def test_keyword_generation(self):
        keyword = generate_keyword()
        self.assertIsNotNone(keyword)
        self.assertIsInstance(keyword, str)

if __name__ == '__main__':
    unittest.main()
