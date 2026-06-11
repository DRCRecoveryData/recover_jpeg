# JPEG Ransomware Recovery Tool

> ⚠️ **CRITICAL WARNING:** Always back up your encrypted files to a completely separate folder before running this utility. The author assumes no responsibility for data loss or file modification accidents.

---

## 📌 Overview

This utility is specifically designed to salvage JPEG photographs that have had their headers destroyed, corrupted, or targeted by ransomware encryption.

If your camera photos were hit by a ransomware variant that only targets the first **150 KB** of each file, the vast majority of your actual image data is still completely intact! This tool extracts that surviving raw bitstream and matches it with a healthy donor header to rebuild a fully viewable photo.

---

## ⚙️ How It Works

A standard JPEG image is split into two major sections:

1. **The Header Metadata:** Contains the camera settings, color profiles, resolution tables, and quantization data.
2. **The Entropy Bitstream:** The actual image content, which begins immediately following the `0xFFDA` (**Start of Scan / SOS**) marker.

Because ransomware typically only encrypts the initial kilobytes of a file, the critical SOS bitstream survives. This tool isolates the healthy payload data from the broken file, grafts it directly onto the valid headers of an unencrypted "model" file, and reconstructs a functional JPEG container wrapper.

```
[ Encrypted First 150KB ] + [ SURVIVING RAW SOS BITSTREAM ]
                                      │
       ┌──────────────────────────────┘
       ▼
[ HEALTHY DONOR HEADER ]  + [ SURVIVING RAW SOS BITSTREAM ] = SUCCESSFUL RECOVERY!

```

---

## 🚀 How to Use

### Step 1: Set Up Your Donor Models

1. Beside the executable script, create a folder named exactly `__models__`.
2. Fill this folder with a small collection of **healthy, unencrypted photographs** taken directly from the exact same camera or phone that shot the broken pictures.
3. *Crucial:* Include models that match every setting combination your camera used (e.g., different resolutions, aspect ratios, quality profiles, and landscape vs. portrait orientations).

### Step 2: Run the Recovery Pipeline

* **Drag and Drop:** Simply drag your corrupted file (e.g., `.JPG.nppp`) and drop it directly onto the executable script.
* **Batch Processing:** The tool will automatically cycle your corrupted bitstream through *every single model* inside your `__models__` folder.
* **Reviewing Outputs:** It will generate multiple output variations side-by-side. While many variations will look like scrambled noise due to layout mismatches, **the single file that perfectly matches the resolution and orientation of your donor model will cleanly decode.**

### Step 3: Managing Stream Padding & 8x8 Alignment

If the ransomware completely zeroed out or cut into your original SOS marker blocks, the script will automatically strip the broken 150 KB header chunk and prompt you for a **Padding Value**.

* **Why padding is requested:** JPEG decoders read image rows sequentially using Minimum Coding Units (MCUs). If bits are missing from the beginning of the stream, subsequent rows shift out of alignment.
* **The Magic Numbers:** Depending on how heavily your camera compresses color metadata, try entering these precise structural blocks when prompted to realign mismatched mountain lines or horizons:

---

## 💬 Author's Note

I built this utility out of absolute necessity after falling victim to a ransomware attack that locked away years of personal memories. Realizing the encryption loop was lazy and left the core payload untouched gave me the key to piece my photos back together. I am sharing this script in the hope that it helps you reclaim your stolen memories just like it did for me!
