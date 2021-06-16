import os

INPUT_STRIPPED_LIST = 'Season2OtherStripped.txt'
DOWNLOAD_LIST = 'download.txt'
FILE_LIST = "finalinput.txt"
OUTPUT_VIDEO = 'finaloutput.mp4'
FONT_FILE = '/home/backup/Bureau_Grot-Book.ttf'
TWITCH_DL = "twitch-dl"
RAW_CLIPS = "rawclips"
WATERMARK_CLIPS = "watermarkclips"
SCRAPE_INFO_NAME = "ScrapeInfo.sh"
SCRAPE_INFO_BASH = """mkdir {RAW_CLIPS}
cd {RAW_CLIPS}
while read p; do
  eval "../{TWITCH_DL} download -q source --overwrite --no-color $p"
done <../{INPUT_STRIPPED_LIST}""".format(RAW_CLIPS=RAW_CLIPS,
    TWITCH_DL=TWITCH_DL, INPUT_STRIPPED_LIST=INPUT_STRIPPED_LIST)
ADD_WATERMARK_UNFORMATTED = """ffmpeg -i {INPUT_PATH} -vf
 drawtext=\"fontfile={FONT_FILE}: text='{CLIP_NAME}':
 fontcolor=white: fontsize=24: box=1: boxcolor=black@0.5:
 boxborderw=5: x=5: y=(h-text_h-5)\" -c:a aac -strict -2
 -ar 44100 -r 60 {OUTPUT_PATH}""".replace('\n','')

# Download each Twitch clip
scrape_info_file = open(SCRAPE_INFO_NAME, "w")
scrape_info_file.write(SCRAPE_INFO_BASH)
scrape_info_file.close()

os.system('bash {SCRAPE_INFO_NAME} > {DOWNLOAD_LIST}'.format(
    SCRAPE_INFO_NAME=SCRAPE_INFO_NAME, DOWNLOAD_LIST=DOWNLOAD_LIST))

print("Finished downloading clips.")

# Add title watermark on each Twitch clip
# And also convert audio to 44100 Hz if needed
download_list_file = open(DOWNLOAD_LIST, "r")
clip_paths = []
clip_name = ""
clip_path = ""

os.system("mkdir {WATERMARK_CLIPS}".format(
    WATERMARK_CLIPS=WATERMARK_CLIPS))

for line in download_list_file:
    if line[0:7] == "Found: ":
        line_split = line.split()
        # Lazily parse name
        for i in range(len(line_split)-1):
            if line_split[i] == "by" and line_split[i+1][-1] == ",":
                clip_name = " ".join(line_split[1:i]).replace(
                    '%', '\\\\\\%').replace('!', '\\!').replace(
                    '\'', '\\’').replace('"', '\\"').replace(':', '\\:')
                break
    elif line[0:12] == "Downloaded: ":
        # Parse path and add watermark
        clip_path = line[12:-1]
        clip_paths.append(clip_path)
        input_path = "{}/{}".format(RAW_CLIPS, clip_path)
        output_path = "{}/{}".format(WATERMARK_CLIPS, clip_path)
        os.system(ADD_WATERMARK_UNFORMATTED.format(INPUT_PATH=input_path,
            FONT_FILE=FONT_FILE, CLIP_NAME=clip_name, OUTPUT_PATH=output_path))
        print("Converted {clip_name}.".format(clip_name=clip_name))
        # Remove raw clips for space
        os.system("rm -f {INPUT_PATH}".format(INPUT_PATH=input_path))

download_list_file.close()

# Remove raw clips for space
os.system("rm -rf {RAW_CLIPS}".format(RAW_CLIPS=RAW_CLIPS))

file_list_file = open(FILE_LIST, "w")
for clip_path in clip_paths:
    file_list_file.write("file '{WATERMARK_CLIPS}/{clip_path}'\n".format(
        WATERMARK_CLIPS=WATERMARK_CLIPS, clip_path=clip_path))
file_list_file.close()

# Final conversion
os.system("ffmpeg -f concat -i {FILE_LIST} -c copy {OUTPUT_VIDEO}".format(
    FILE_LIST=FILE_LIST, OUTPUT_VIDEO=OUTPUT_VIDEO))
print("Conversion done!")