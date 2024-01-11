# Note

This document is currently outdated.

# How It Does

As of now the program basically takes the **white** background, subtracts it from the base image, finds remaining parts, and saves them into separate files in random order. Due to this basic approach there are many obstacles that this method is prone to, here are some possible things to consider:

1. Unaligned Panel Borders
2. Different Sized Panels
3. Panels On Edge
4. Tilted Panel Separators
5. Non-Straight Panel Separators
6. Joint Panels
7. Overlapping Panels
8. Colored Background
9. Image Background
10. Overflown Speech Bubble
11. Overflown Text
12. Overflown Panel Item
13. Borderless Panels

They are ordered as increasingly complex to handle. The current method can handle the first three (3) problems almost perfectly, and up to first five (5) of them you can use this program with expectations of it working with a high success rate.

## How It Handles These

For 6 and 7 the panels that are joint or overlapping will be saved together as they are treated as one single panel.

For 8 and 9 either the base image will be saved as is without any changes or if there is a big enough white spot in any of the panels, it will be treated as background, resulting in the base image without that part.

For 10, 11, and 12 as long as the overflowing object does not cut the white background the program will work normally. But whenever the overflown object cuts the white background, meaning it's connecting at least two (2) panels together, the program will produce some unseparated panel image files.

For 13 I couldn't find a test page but it will most likely find the panel but it will be saved lacking some white part of it, cropping it wrong etc.

## Notes

Right now a deep learning approach is considered to get better results, but some parts of this idea is unclear.

The current way of working of this program was based on this [paper](based-paper.pdf).

# What It Does

Here you can see some examples, with each problem mentioned:

- Simplest case, no complexities, this is as easy as it gets\
   Input:\
   ![](/test-in/simple.jpg)\
   Outputs:
  - ![](/test-out/simple_0.jpg)
  - ![](/test-out/simple_1.jpg)\
    Here you can see these two panels are not separated, this goes to show that even when the issues mentioned above are not encountered there are other more general problems regards to image processing, in this case there happens to be a gray-ish spot in between on the left side of these panels for some reason.
  - ![](/test-out/simple_2.jpg)
  - ![](/test-out/simple_3.jpg)
  - ![](/test-out/simple_4.jpg)
  - ![](/test-out/simple_5.jpg)
- Unaligned Panel Borders and Different Sized Panels example:\
   Input:\
   ![](/test-in/1-2.jpg)\
   Outputs:
  - ![](/test-out/1-2_0.jpg)
  - ![](/test-out/1-2_1.jpg)
  - ![](/test-out/1-2_2.jpg)
  - ![](/test-out/1-2_3.jpg)
  - ![](/test-out/1-2_4.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge example:\
  Input:\
  ![](</test-in/1-2-3%20(1).jpg>)\
  Outputs:
  - ![](</test-out/1-2-3%20(1)_0.jpg>)
  - ![](</test-out/1-2-3%20(1)_1.jpg>)
  - ![](</test-out/1-2-3%20(1)_2.jpg>)
  - ![](</test-out/1-2-3%20(1)_3.jpg>)
  - ![](</test-out/1-2-3%20(1)_4.jpg>)
  - ![](</test-out/1-2-3%20(1)_5.jpg>)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge example:\
  Input:\
  ![](</test-in/1-2-3%20(2).jpg>)\
  Outputs:
  - ![](</test-out/1-2-3%20(2)_0.jpg>)
  - ![](</test-out/1-2-3%20(2)_1.jpg>)
  - ![](</test-out/1-2-3%20(2)_2.jpg>)
  - ![](</test-out/1-2-3%20(2)_3.jpg>)
  - ![](</test-out/1-2-3%20(2)_4.jpg>)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Overflown Speech Bubble, Overflown Panel Item example:\
  Input:\
  ![](/test-in/1-2-3-10-12.jpg)\
  Outputs:
  - ![](/test-out/1-2-3-10-12_0.jpg)
  - ![](/test-out/1-2-3-10-12_1.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Overflown Speech Bubble example:\
  Input:\
  ![](/test-in/1-2-3-10.jpg)\
  Outputs:
  - ![](/test-out/1-2-3-10_0.jpg)
  - ![](/test-out/1-2-3-10_1.jpg)
  - ![](/test-out/1-2-3-10_2.jpg)
  - ![](/test-out/1-2-3-10_3.jpg)
  - ![](/test-out/1-2-3-10_4.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators, Overflown Speech Bubble, Overflown Panel Item example:\
  Input:\
  ![](/test-in/1-2-3-4-10-12.jpg)\
  Outputs:
  - ![](/test-out/1-2-3-4-10-12_0.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators, Overflown Speech Bubble example:\
  Input:\
  ![](/test-in/1-2-3-4-10.jpeg)\
  Outputs:
  - ![](/test-out/1-2-3-4-10_0.jpeg)
  - ![](/test-out/1-2-3-4-10_1.jpeg)
  - ![](/test-out/1-2-3-4-10_2.jpeg)
  - ![](/test-out/1-2-3-4-10_3.jpeg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators, Overflown Text, Overflown Panel Item example:\
  Input:\
  ![](/test-in/1-2-3-4-11-12.jpg)\
  Outputs:
  - ![](/test-out/1-2-3-4-11-12_0.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators, Non-Straight Panel Separators, Joint Panels, Overlapping Panels, Colored Background, Overflown Panel Item example:\
  Input:\
  ![](/test-in/1-2-3-4-5-6-7-8-12.jpeg)\
  Outputs:
  - ![](/test-out/1-2-3-4-5-6-7-8-12_0.jpeg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators, Non-Straight Panel Separators, Colored Background, Overflown Speech Bubble example:\
  Input:\
  ![](/test-in/1-2-3-4-5-8-10.jpeg)\
  Outputs:
  - ![](/test-out/1-2-3-4-5-8-10_0.jpeg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators, Overlapping Panels, Overflown Speech Bubble example:\
  Input:\
  ![](/test-in/1-2-3-4-7-10.jpg)\
  Outputs:
  - ![](/test-out/1-2-3-4-7-10_0.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators, Colored Background, Overflown Panel Item example:\
  Input:\
  ![](/test-in/1-2-3-4-8-12.jpg)\
  Outputs:
  - ![](/test-out/1-2-3-4-8-12_0.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge, Tilted Panel Separators example:\
  Input:\
  ![](/test-in/1-2-3-4.jpg)\
  Outputs:
  - ![](/test-out/1-2-3-4_0.jpg)
  - ![](/test-out/1-2-3-4_1.jpg)
  - ![](/test-out/1-2-3-4_2.jpg)
  - ![](/test-out/1-2-3-4_3.jpg)
- Unaligned Panel Borders, Different Sized Panels, Panels On Edge example:\
  Input:\
  ![](/test-in/1-2-3.jpg)\
  Outputs:
  - ![](/test-out/1-2-3_0.jpg)
  - ![](/test-out/1-2-3_1.jpg)
  - ![](/test-out/1-2-3_2.jpg)
- Different Sized Panels, Overflown Speech Bubble, Overflown Text, Overflown Panel Item example:\
  Input:\
  ![](/test-in/2-10-11-12.jpg)\
  Outputs:
  - ![](/test-out/2-10-11-12_0.jpg)
  - ![](/test-out/2-10-11-12_1.jpg)
  - ![](/test-out/2-10-11-12_2.jpg)
  - ![](/test-out/2-10-11-12_3.jpg)
  - ![](/test-out/2-10-11-12_4.jpg)
  - ![](/test-out/2-10-11-12_5.jpg)
