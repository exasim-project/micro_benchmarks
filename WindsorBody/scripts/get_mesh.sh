#!/bin/sh

wget https://drive.google.com/uc\?export=download\&id\=18V6h0fjRzTxV8g6ZqSAzqGmopvfyoDRN\&confirm\=t\&uuid=7d2a21bb-0257-4538-bc8b-9d2556b59773\&at\=AHV7M3eU5WdaCruYj48EJRGr3DkK:1668419843949 -O polyMesh.tar.lzma
tar xvf polyMesh.tar.lzma
mv polyMesh constant
rm -rf polyMesh.tar.lzma
