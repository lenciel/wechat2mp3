#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import subprocess
import datetime


def is_silk_file(file_path):
    input_file = open(file_path, 'rb')
    header = input_file.read(10)
    silk_header = b'#!SILK_V3'
    input_file.close()
    return header[1:] == silk_header


def convert_amr_file(input_dir, input_file_name, output_dir):
    # These files are AMR files without the AMR header,
    # so they can be converted by just adding the AMR file header
    # and then converting from AMR to WAV.

    input_file_path = os.path.join(input_dir, input_file_name);
    input_file = open(input_file_path, 'rb')

    intermediate_file_name = input_file_name.replace(".aud", ".amr")
    intermediate_file_path = os.path.join(output_dir, intermediate_file_name)
    intermediate_file = open(intermediate_file_path, 'wb')

    header_file_path = "amr_header/amr_header.bin"
    header_file = open(header_file_path, 'rb')
    intermediate_file.write(header_file.read() + input_file.read())

    input_file.close()
    intermediate_file.close()
    header_file.close()

    wav_output_file_name = input_file_name.replace(".aud", ".wav")
    wav_output_file_path = os.path.join(output_dir, wav_output_file_name)
    mp3_output_file_name = input_file_name.replace(".aud", ".mp3")
    mp3_output_file_path = os.path.join(output_dir, wav_output_file_name)

    black_hole_file = open("black_hole", "w")
    subprocess.call(["ffmpeg", "-i", intermediate_file_path, wav_output_file_path],
                    stdout=black_hole_file, stderr=black_hole_file)
    subprocess.call(["ffmpeg", "-i", wav_output_file_path, "-f", "mp2", mp3_output_file_path],
                    stdout=black_hole_file, stderr=black_hole_file)
    black_hole_file.close()

    # Delete the junk files
    os.remove("black_hole")
    os.remove(intermediate_file_path)


def convert_silk_file(input_dir, input_file_name, decoder_file_path, output_dir):
    # These files are encoded with the SILK codec, originally developed by Skype. They can be
    # converted by stripping out the first byte and then using the SILK decoder.

    input_file_path = os.path.join(input_dir, input_file_name);
    input_file = open(input_file_path, 'rb')

    intermediate_file_1_name = input_file_name.replace(".aud", ".silk")
    intermediate_file_1_path = os.path.join(output_dir, intermediate_file_1_name)
    intermediate_file_1 = open(intermediate_file_1_path, 'wb')

    # WeChat adds a single extra byte before their SILK files. We need to strip it out.
    intermediate_file_1.write(input_file.read()[1:])

    input_file.close()
    intermediate_file_1.close()

    intermediate_file_2_name = input_file_name.replace(".aud", ".pcm")
    intermediate_file_2_path = os.path.join(output_dir, intermediate_file_2_name)
    intermediate_file_2 = open(intermediate_file_2_path, 'wb')

    intermediate_file_3_name = input_file_name.replace(".aud", ".wav")
    intermediate_file_3_path = os.path.join(output_dir, intermediate_file_3_name)
    mp3_output_file_name = input_file_name.replace(".aud", ".mp3")
    mp3_output_file_path = os.path.join(output_dir, mp3_output_file_name)

    black_hole_file = open("black_hole", "w")

    # Use the SILK decoder to convert it to PCM
    subprocess.call([decoder_file_path, intermediate_file_1_path, intermediate_file_2_path],
                    stdout=black_hole_file, stderr=black_hole_file)

    # And then ffmpeg to convert that to wav
    subprocess.call(["ffmpeg", "-f", "s16le", "-ar", "24000",
                    "-i", intermediate_file_2_path, intermediate_file_3_path],
                    stdout=black_hole_file, stderr=black_hole_file)

    # And then ffmpeg to convert to MP3
    subprocess.call(["ffmpeg", "-i", intermediate_file_3_path,
                    "-f", "mp2", mp3_output_file_path],
                    stdout=black_hole_file, stderr=black_hole_file)
    black_hole_file.close()
    intermediate_file_2.close()

    # Delete the junk files
    os.remove("black_hole")
    os.remove(intermediate_file_1_path)
    os.remove(intermediate_file_2_path)
    os.remove(intermediate_file_3_path)


class Main(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):

        audio_src = values
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        converted = now + "_converted"
        os.mkdir(converted)

        try:
            # Decide which one of these are AMR files and which are SILK, and then convert.
            for dirname, dirnames, filenames in os.walk(audio_src):
                for filename in filenames:
                    if filename[0] == '.': continue
                    input_path = os.path.join(dirname, filename)
                    if (is_silk_file(input_path)):
                        convert_silk_file(dirname, filename, namespace.silk_decoder, converted)
                    else:
                        convert_amr_file(dirname, filename, converted)

            print("Done!")
        except:
            print("Something went wrong converting the audio files.\n"
                "Common problems:\n"
                "You may be missing the dependencies (ffmpeg and/or the SILK codec decoder).\n"
                "The decoder (and its dependencies) must be in the specified path.\n"
                "The SILK codec decoder also can't handle very large file paths.\n"
                "Try a shorter path to your input directory.")


parser = argparse.ArgumentParser(description=".aud converter: convert wechat .aud files into .wav",
        epilog="This script is an open source tool under the GNU GPLv3 license. Uses content "\
                "modified from a tool originally for DEFT 8.")
parser.add_argument("Folder", action=Main, help=".aud files root folder.")
parser.add_argument("-s", "--silk-decoder", nargs="?", default="./decoder",
        help="Path to the SILK codec decoder program.")

args = parser.parse_args()
