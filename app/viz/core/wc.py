from django.conf import settings
import os
import re
import numpy as np
from konlpy.tag import Mecab
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image

__all__ = [
    'gen_wc_png',
]


def gen_wc_png(
        data,
        stopwords=None,
        word_len_min=1,
        max_word_size=100,
        bg_color='white',
        font=None,
        mask=None,
        mask_coloring=True,
):
    """Generate wc png file
    :param str data:
    :param int max_word_size:
    :param int word_len_min:
    :param str bg_color:
    :param django.core.files.uploadedfile.TemporaryUploadedFile mask:
    :param bool mask_coloring:
    :param django.core.files.uploadedfile.TemporaryUploadedFile font:
    :param str stopwords: Stopwords separated ','
    :return: none
    """
    data = re.sub(r'\W', ' ', data)  # Use regular expression for data scailing

    nlp = Mecab('/usr/local/lib/mecab/dic/mecab-ko-dic')  # Make Mecab(NLP) object

    data_nouns = nlp.nouns(data)  # Extract nouns from data and input it to data_nouns
    data_nouns_cnt = Counter(data_nouns)  # Count nouns from data_nouns and make it dict type data

    # Stop Words Process
    if stopwords:
        stopwords = stopwords.replace(' ', '')
        stopwords = stopwords.split(',')
        for word in stopwords:
            del data_nouns_cnt[word]

    # Minimum Word Length Process
    if word_len_min > 1:
        word_len_min_del_list = list()
        for word in data_nouns_cnt:
            if len(word) < word_len_min:
                word_len_min_del_list.append(word)
        for word in word_len_min_del_list:
            del data_nouns_cnt[word]

    # Set Font
    if font: wc_font = font.temporary_file_path()
    else: wc_font = os.path.join(settings.ROOT_DIR, 'extension/fonts/DOSGothic.ttf')

    # Set Image Mask
    if mask: wc_mask = np.array(Image.open(mask))
    else: wc_mask = np.array(Image.open(os.path.join(settings.ROOT_DIR, 'extension/wc_mask/default.png')))

    wc = WordCloud(
        max_font_size=max_word_size,
        background_color=bg_color,
        font_path=wc_font,
        mask=wc_mask,
    ).generate_from_frequencies(data_nouns_cnt)

    if mask_coloring:
        mask_colors = ImageColorGenerator(wc_mask)
        plt.figure(figsize=(40, 20), dpi=55)
        plt.imshow(wc.recolor(color_func=mask_colors), interpolation="bilinear")
    else:
        plt.figure(figsize=(40, 20), dpi=55)
        plt.imshow(wc, interpolation="bilinear")

    plt.axis('off')

    if not os.path.exists(settings.VIZ_DIR):
        os.makedirs(settings.VIZ_DIR, exist_ok=True)
    plt.savefig(os.path.join(settings.VIZ_DIR, 'wc.png'), bbox_inches='tight')
    plt.close()
