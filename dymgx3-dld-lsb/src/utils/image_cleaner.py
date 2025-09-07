from email.mime import base
import os
import glob
from pathlib import Path
from typing import List, Optional


class ImageCleaner:
    """图片删除工具类，用于删除指定文件夹下的所有图片文件"""

    SUPPORTED_IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".tif",
        ".webp",
        ".svg",
        ".ico",
        ".psd",
        ".raw",
        ".heic",
        ".avif",
    }

    def __init__(self, folder_path: str):
        """
        初始化图片清理器

        Args:
            folder_path: 要清理图片的文件夹路径
        """
        self.folder_path = Path(folder_path)
        if not self.folder_path.exists():
            raise FileNotFoundError(f"文件夹不存在: {folder_path}")
        if not self.folder_path.is_dir():
            raise NotADirectoryError(f"路径不是文件夹: {folder_path}")

    def find_images(self, recursive: bool = True) -> List[Path]:
        """
        查找文件夹中的所有图片文件

        Args:
            recursive: 是否递归搜索子文件夹

        Returns:
            图片文件路径列表
        """
        images = []
        search_pattern = "**/*" if recursive else "*"

        for file_path in self.folder_path.glob(search_pattern):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.SUPPORTED_IMAGE_EXTENSIONS
            ):
                images.append(file_path)

        return sorted(images)

    def delete_images(self, recursive: bool = True, dry_run: bool = False) -> dict:
        """
        删除文件夹中的所有图片文件

        Args:
            recursive: 是否递归删除子文件夹中的图片
            dry_run: 是否为试运行模式（只显示要删除的文件，不实际删除）

        Returns:
            包含删除结果的字典
        """
        images = self.find_images(recursive=recursive)

        if not images:
            return {
                "total_found": 0,
                "deleted": 0,
                "failed": 0,
                "files": [],
                "errors": [],
            }

        deleted_files = []
        failed_files = []
        errors = []

        for image_path in images:
            try:
                if not dry_run:
                    image_path.unlink()
                deleted_files.append(str(image_path))
            except Exception as e:
                failed_files.append(str(image_path))
                errors.append(f"删除 {image_path} 失败: {str(e)}")

        return {
            "total_found": len(images),
            "deleted": len(deleted_files),
            "failed": len(failed_files),
            "files": deleted_files,
            "errors": errors,
            "dry_run": dry_run,
        }

    def get_image_info(self, recursive: bool = True) -> dict:
        """
        获取文件夹中图片文件的信息

        Args:
            recursive: 是否递归搜索子文件夹

        Returns:
            包含图片信息的字典
        """
        images = self.find_images(recursive=recursive)

        total_size = 0
        extension_count = {}

        for image_path in images:
            try:
                size = image_path.stat().st_size
                total_size += size

                ext = image_path.suffix.lower()
                extension_count[ext] = extension_count.get(ext, 0) + 1
            except Exception:
                continue

        return {
            "total_count": len(images),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "extension_breakdown": extension_count,
            "files": [str(img) for img in images],
        }


def delete_images_from_folder(
    folder_path: str, recursive: bool = True, dry_run: bool = False
) -> dict:
    """
    便捷函数：删除指定文件夹下的所有图片

    Args:
        folder_path: 文件夹路径
        recursive: 是否递归删除子文件夹中的图片
        dry_run: 是否为试运行模式

    Returns:
        删除结果字典
    """
    cleaner = ImageCleaner(folder_path)
    return cleaner.delete_images(recursive=recursive, dry_run=dry_run)


def get_folder_image_info(folder_path: str, recursive: bool = True) -> dict:
    """
    便捷函数：获取文件夹中的图片信息

    Args:
        folder_path: 文件夹路径
        recursive: 是否递归搜索子文件夹

    Returns:
        图片信息字典
    """
    cleaner = ImageCleaner(folder_path)
    return cleaner.get_image_info(recursive=recursive)


def print_image_info(folder_path: str, recursive: bool = True):
    """
    打印文件夹中图片信息的函数

    Args:
        folder_path: 文件夹路径
        recursive: 是否递归搜索子文件夹
    """
    try:
        info = get_folder_image_info(folder_path, recursive=recursive)
        print(f"文件夹: {folder_path}")
        print(f"图片总数: {info['total_count']}")
        print(f"总大小: {info['total_size_mb']} MB")
        print(f"文件类型分布: {info['extension_breakdown']}")
        if info["files"]:
            print("\n找到的图片文件:")
            for file in info["files"]:
                print(f"  {file}")
    except Exception as e:
        print(f"错误: {e}")


def clean_images(folder_path: str, recursive: bool = True, dry_run: bool = False):
    """
    清理文件夹中图片的函数

    Args:
        folder_path: 文件夹路径
        recursive: 是否递归删除子文件夹中的图片
        dry_run: 是否为试运行模式
    """
    try:
        result = delete_images_from_folder(
            folder_path, recursive=recursive, dry_run=dry_run
        )

        if dry_run:
            print(
                f"[试运行模式] 在文件夹 {folder_path} 中找到 {result['total_found']} 个图片文件"
            )
            if result["files"]:
                print("\n将要删除的文件:")
                for file in result["files"]:
                    print(f"  {file}")
        else:
            print(f"删除完成！")
            print(f"找到图片: {result['total_found']} 个")
            print(f"成功删除: {result['deleted']} 个")
            if result["failed"] > 0:
                print(f"删除失败: {result['failed']} 个")
                print("错误详情:")
                for error in result["errors"]:
                    print(f"  {error}")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    delete_images_from_folder("./数据")
