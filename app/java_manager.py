import logging
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

class JavaManager:
    def __init__(self):
        self.versions = {
            "8": "https://api.adoptium.net/v3/binary/latest/8/ga/linux/{arch}/jdk/hotspot/normal/eclipse?project=jdk",
            "11": "https://api.adoptium.net/v3/binary/latest/11/ga/linux/{arch}/jdk/hotspot/normal/eclipse?project=jdk",
            "17": "https://api.adoptium.net/v3/binary/latest/17/ga/linux/{arch}/jdk/hotspot/normal/eclipse?project=jdk",
            "21": "https://api.adoptium.net/v3/binary/latest/21/ga/linux/{arch}/jdk/hotspot/normal/eclipse?project=jdk"
        }

    def get_arch(self):
        arch = platform.machine().lower()
        if arch in ["x86_64", "amd64"]:
            return "x64"
        elif arch in ["aarch64", "arm64"]:
            return "aarch64"
        elif "arm" in arch:
            return "arm"
        return arch

    def download_java(self, version: str, install_dir: Path) -> Path:
        arch = self.get_arch()
        if version not in self.versions:
            raise ValueError(f"サポートされていないJavaバージョンです: {version}")

        url = self.versions[version].format(arch=arch)
        java_dir = install_dir / "bin" / f"java-{version}"
        java_dir.mkdir(parents=True, exist_ok=True)
        
        tar_path = install_dir / f"java-{version}.tar.gz"
        
        print(f"\nJava {version} ({arch}) をダウンロードしています...")
        logger.info("Java %s (%s) を %s からダウンロードしています", version, arch, url)
        
        try:
            urllib.request.urlretrieve(url, tar_path)
            
            print("アーカイブを解凍しています...")
            logger.info("Javaアーカイブを解凍しています: %s", tar_path)
            
            with tarfile.open(tar_path, "r:gz") as tar:
                # 抽出先を制御するためにメンバーリストを処理
                members = tar.getmembers()
                # 最初のディレクトリ名を取得
                root_dir = members[0].name.split('/')[0]
                tar.extractall(path=install_dir / "bin")
            
            # 抽出されたディレクトリをリネーム
            extracted_dir = install_dir / "bin" / root_dir
            if extracted_dir.exists():
                if java_dir.exists():
                    shutil.rmtree(java_dir)
                extracted_dir.rename(java_dir)
            
            tar_path.unlink()
            print(f"Java {version} のインストールが完了しました。")
            logger.info("Java %s のインストールが完了しました: %s", version, java_dir)
            
            return java_dir / "bin" / "java"
            
        except Exception as e:
            logger.exception("Javaのダウンロードまたは解凍中にエラーが発生しました", exc_info=e)
            print(f"Javaのインストール中にエラーが発生しました: {e}")
            if tar_path.exists():
                tar_path.unlink()
            return None

java_manager = JavaManager()
