from PIL import Image, ImageDraw, ImageFont
import ffmpeg
import os

def generate_video(summary, output_filename="output.mp4"):
    try:
        words = summary.split()[:50]  # Limit to 50 words
        text = " ".join(words)

        # Create an image with text
        img = Image.new("RGB", (1280, 720), color="black")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 40)  # Load font
        except:
            font = ImageFont.load_default()  # Use default if unavailable

        draw.text((100, 300), text, font=font, fill="white")

        img.save("frame.png")  # Save image frame

        # Generate a 10-sec video using ffmpeg
        os.system(f"ffmpeg -loop 1 -i frame.png -c:v libx264 -t 10 -pix_fmt yuv420p {output_filename}")

        # Cleanup
        os.remove("frame.png")

        return output_filename

    except Exception as e:
        return f"❌ Video generation failed: {e}"

# Example Usage
if __name__ == "__main__":
    test_summary = "This is a robust video generator using ffmpeg and PIL."
    result = generate_video(test_summary)
    print("Generated Video:", result)
