# Manga Panel Extractor

A simple program that takes manga pages and outputs panels on them. The current way of working of this program was inspired from this [paper](related-paper.pdf). Thanks to Xufang Pang, Ying Cao, Rynson W.H. Lau, and Antoni B. Chan for their work.

Please read [report](reports\internal\report.pdf) for detailed explanation of the implemented algorithm(s).

- Please note that this program is designed specifically for manga and may not work correctly with manhwas or other similar formats.

## Installation

Visit the [Releases](https://github.com/adenzu/Manga-Panel-Extractor/releases) section of the repository and download the executable for Windows. Currently, only the Windows7+ versions are supported. However, you can build for other platforms using the provided source code.

## Usage

### Website
1. Go to the website https://adenzu.github.io/Manga-Panel-Extractor/
2. Select image files of manga pages you want to extract panels of
3. Click `Start`
4. Click `Cancel` to cancel panel extraction process whenever you want to
5. Click `Download` to download a zip file containing all the panels

- **Note:** Too many images may cause computer lag.

### Executable

0. You can check examples in advance to see if this program can help you with your images, see examples [here](tests\data\test_performance\README.md#what-it-does).
1. [Download the latest executable](https://github.com/adenzu/Manga-Panel-Extractor/releases/latest) for your operating system.
2. Execute the downloaded executable.
3. Select the input directory containing the manga page images. Each image should represent one manga page.
4. Choose the output directory where the extracted panels will be saved.
5. You can check the checkbox named "Split Joint Panels" to split joint panels. **This slows down the process up to ten fold.**
6. You can check the checkbox named "Fallback" for fallback method to be applied in case of a failed extraction.
7. You can check the checkbox named "Output to Separate Folders" to extract each image's panels into their respective folder.
8. Click "Start" to initiate the panel extraction process. You can monitor the progress in the bottom left corner of the program window.
9. To cancel the process, click "Cancel".

- Please note that this program is designed specifically for manga and may not work correctly with manhwas or other similar formats.

### CLI - Input and Output Directories

```bash
python main.py [input_dir] [output_dir] [-s] [-f] [-g]
```

or

```bash
python main.py [input_img_path] [-s] [-f] [-g]
```

- `[input_img_path]`: Input image path.
- `[input_dir]`: Input directory.
- `[output_dir]` (optional): Output directory.
- `-s` or `--split-joint-panels` (optional): Split joint panels.
- `-f` or `--fallback` (optional): Fallback to a more aggressive method if the first one fails.
- `-g` or `--gui` (optional): Use GUI.

## Program Explanation and Examples

See explanation and examples [here](tests\data\test_performance\README.md).

## Features

The key feature of Manga Panel Extractor is its ability to analyze manga pages and extract panels from them.

## Configuration

Manga Panel Extractor does not require any additional configuration. It is ready to use out of the box.

## Contributing

Currently, there is limited community involvement in this project. Feel free to contribute by submitting bug reports or feature requests through the [Issues](https://github.com/adenzu/Manga-Panel-Extractor/issues) section.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Troubleshooting

- If the extraction process is unsuccessful, the output image may resemble the input manga page image itself.

## Contact

If you have any questions, issues, or suggestions, please open an issue in the [Issues](https://github.com/adenzu/Manga-Panel-Extractor/issues) section.
