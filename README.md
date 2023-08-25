# Manga Panel Extractor

A simple program that takes manga pages and outputs panels on them. The current way of working of this program was based on this [paper](based-paper.pdf). Thanks to Xufang Pang, Ying Cao, Rynson W.H. Lau, and Antoni B. Chan for their work.

## Installation

Visit the [Releases](https://github.com/adenzu/Manga-Panel-Extractor/releases) section of the repository and download the executable for Windows. Currently, only the Windows version is supported. However, you can build for other platforms using the provided source code.

## Usage

### Executable

0. You can check examples in advance to see if this program can help you with your images, see examples [here](INSIGHT.md#what-it-does).
1. [Download the latest executable](https://github.com/adenzu/Manga-Panel-Extractor/releases/tag/v1.0.0) for your operating system.
2. Execute the downloaded executable.
3. Select the input directory containing the manga page images. Each image should represent one manga page.
4. Choose the output directory where the extracted panels will be saved.
5. Click "Start" to initiate the panel extraction process. You can monitor the progress in the bottom left corner of the program window.
6. To cancel the process, click "Cancel".

- Please note that this program is designed specifically for manga and may not work correctly with manhwas or other similar formats.

### CLI - Input and Output Directories

```bash
python main.py <input_dir> <output_dir>
```

### CLI - Single Image

```bash
python main.py <image_path>
```

## Program Explanation and Examples

See explanation and examples [here](INSIGHT.md).

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
