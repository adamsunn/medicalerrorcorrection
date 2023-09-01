# Automatic Speech Recognition Error Correction on ICU Clinical Narration Dataset
CS 224N Final Project

Code based on [ConstDecoder](https://github.com/yangjingyuan/ConstDecoder).

Automatic Speech Recognition (ASR) in clinical settings is gaining popularity as clear communication is critical in healthcare delivery. Scenarios in intensive care units (ICUs) are more complex, involving obscure medical terminology and noisy environments. Corrections or adaptations to certain domains are needed to make the narrations more reliable. 

In this paper, we aimed to create an ASR error corrector using a small dataset of nurse-corrected ICU-clinical narration transcribed by Whisper. Given the limited data, we augmented the Mtsamples dataset and pretrained a ConstDecoder model on our augmented dataset, finetuning the model on our own nurse-annotated ICU narration correction dataset. Our findings show that our model is able to outperform baselines and reduce the WER by up to 16%, proving the superiority of our approach, and confirming the model's ability to be a reliable and effective error corrector in the ICU.


