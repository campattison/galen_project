#!/usr/bin/env python3
"""Check a rebuilt on_mixtures.txt against the file used in the evaluation.

    python3 mt_eval/input/check_references.py path/to/rebuilt/on_mixtures.txt
    python3 mt_eval/input/check_references.py --pre-fix path/to/rebuilt/mixtures_pre_fix/on_mixtures.txt

The published English of On Mixtures is not distributed with this repository (see REFERENCES.md in
this folder): each reference paragraph is replaced by a pointer line. Rebuild the file by putting each
translation, as a single line, in place of its pointer. This script then checks the whole file, its
layout (which line is a `Chunk N` line, which is blank, which holds text), the Greek of each passage
and each translation, and reports every difference by passage, translator and sentence, using the
SHA-256 values below (of the line as stored, of the normalized text that REFERENCES.md defines, and of
each sentence). The pre-fix copy is checked against the pre-fix layout when --pre-fix is given or when
the file is in a folder named mixtures_pre_fix; on_comp.txt is recognized by its Greek.

Exit status 0 only if the file is byte-identical to the file used in the evaluation.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

POINTER = b'[reference not distributed; see mt_eval/input/REFERENCES.md]'
FOLD = {**dict.fromkeys(map(ord, '‐‑‒–—―−'), '-'),
        **dict.fromkeys(map(ord, '‘’‚‛ʼ′'), "'"),
        **dict.fromkeys(map(ord, '“”„‟'), '"'),
        **dict.fromkeys(map(ord, '­​‌‍﻿'), None),
        ord('…'): '...'}
SENTENCE_NORMALIZED = re.compile(r'(?<=[.?!]) ')
SENTENCE_RAW = re.compile(r'(?<=[.?!])\s+')
LINE_KIND = {'H': 'Chunk line', 'B': 'blank', 'T': 'text'}


def normalize(text):
    """NFKC; soft hyphen and zero-width characters deleted; dashes, ellipsis and quotes folded;
    whitespace collapsed to single spaces and stripped. Case is kept."""
    return ' '.join(unicodedata.normalize('NFKC', text).translate(FOLD).split())


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def sentences_normalized(text):
    return SENTENCE_NORMALIZED.split(normalize(text))


def sentences_raw(text):
    return SENTENCE_RAW.split(text.strip())


# Per passage: its locators, the SHA-256 of its Greek line and, for each reference translation in slot
# order, its word count, its first three and last three words, and the SHA-256 of the line as stored
# ('raw'), of its normalized text, and of each sentence of each.
MIX = {
    1: {'location': "I.1, 1,1–2,3 H.; I.509,1–510,15 K.",
        'greek': "14c1a5eeb9c4e13b451b654f04c7e7405f44909799a4447de6069a90f31f1c71",
        'refs': [
            {'translator': "Johnston", 'words': 263, 'begins': "That the bodies", 'ends': "of the terms.",
             'raw': "52ce78ab0cddf5ace889f538f5a999cbffc863efdd88f962c77cb800d201320b",
             'normalized': "14499c620239db7bd3d7692af487d2abc22f82787bac866823ac3867f69f5278",
             'sentences_normalized': [
                 "4aec407edc08160004dbd898c114bad898c58867efe56959ac521e713a3b7343",
                 "046cf98714025f2d7c755acd429f14ec19015585984e984b3da3c5e0efc1ddb5",
                 "b9fcddf6917583202eeb8bb2eed43cf21e6ad495f11eeef0666e3d3d30afdcfb",
                 "d55d4c2c2c4a94a69548f105a70f2cf531905199e06a7dc041e286c649e96c73",
                 "6b3dde20f29d253ebe0322c801aa6f4c405445f553d9e7e3af5dc405cefa2668",
                 "7d9efa0350689743821a47cd1a6ab53ac6bf8c8a98b950529b5acfd4be854d18",
                 "940d32a8396648e4065f05d1b930f5399c3ac9f78309197ec709c6e168ee7106",
                 "3bfb004099c1b80b888d429b751a50e3936801fefe9498e9d807a8c6beb82472",
                 "fe0b9c8a4be33da940eb2d3778a2a3ef1f101728aad10afa81b029603797b27d",
                 "1842bba5c38dfc5a5ba7f4fad76428f50e47456c4bf9c0ff74865d5f25f33063",
             ],
             'sentences_raw': [
                 "05eb774bcfff318b8e4463b254d80daf13dc4aa6c2183ce9903ba05b543ed069",
                 "046cf98714025f2d7c755acd429f14ec19015585984e984b3da3c5e0efc1ddb5",
                 "b9fcddf6917583202eeb8bb2eed43cf21e6ad495f11eeef0666e3d3d30afdcfb",
                 "d55d4c2c2c4a94a69548f105a70f2cf531905199e06a7dc041e286c649e96c73",
                 "7ad36d56577ef16c4fc8c6e75249d1f85b06a82c02200ec6d139e3b9e54df62f",
                 "7d9efa0350689743821a47cd1a6ab53ac6bf8c8a98b950529b5acfd4be854d18",
                 "940d32a8396648e4065f05d1b930f5399c3ac9f78309197ec709c6e168ee7106",
                 "3bfb004099c1b80b888d429b751a50e3936801fefe9498e9d807a8c6beb82472",
                 "fe0b9c8a4be33da940eb2d3778a2a3ef1f101728aad10afa81b029603797b27d",
                 "1842bba5c38dfc5a5ba7f4fad76428f50e47456c4bf9c0ff74865d5f25f33063",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 294, 'begins': "That the bodies", 'ends': "terms are used.",
             'raw': "c6e1a049cb61141069639063a2c4e569b71ffad9431c023b671a6e6459eefa62",
             'normalized': "c6e1a049cb61141069639063a2c4e569b71ffad9431c023b671a6e6459eefa62",
             'sentences_normalized': [
                 "9c1becc212586acb7218d29ebb58b9c6f154261e314ead39e925232168b0355c",
                 "1a4ed15b6a25d17f9a4e8ed08ff0d00aad80aef88fb3389199d561afe29179f3",
                 "0735490577be02423443815063ed1916fc07f3c1a9da908a18185b2a0b7d0d66",
                 "81b2f394723ce8901d07b8a1fa57e5ef4c4b6ed4d82b27e050c30ba5428623be",
                 "fb460ed6a88a0e8bd9abe1ca1b0a6950e783e70daa886f3716fe03129c71f32e",
                 "3a8357068b813fcd479193c8fc548037a4a03d066aa7483c9b75265d5e1774b2",
             ],
             'sentences_raw': [
                 "9c1becc212586acb7218d29ebb58b9c6f154261e314ead39e925232168b0355c",
                 "1a4ed15b6a25d17f9a4e8ed08ff0d00aad80aef88fb3389199d561afe29179f3",
                 "0735490577be02423443815063ed1916fc07f3c1a9da908a18185b2a0b7d0d66",
                 "81b2f394723ce8901d07b8a1fa57e5ef4c4b6ed4d82b27e050c30ba5428623be",
                 "fb460ed6a88a0e8bd9abe1ca1b0a6950e783e70daa886f3716fe03129c71f32e",
                 "3a8357068b813fcd479193c8fc548037a4a03d066aa7483c9b75265d5e1774b2",
             ]},
        ]},
    2: {'location': "I.4, 12,13–13,10 H.; I.527,13–529,2 K.",
        'greek': "e32b11359bd1ce0073b2fe45e0f1559fba6c8d8d7bb1c84db8d6b1716e539fd5",
        'refs': [
            {'translator': "Johnston", 'words': 264, 'begins': "And this, the", 'ends': "wet and hot.",
             'raw': "23f0f1f8b0ad47b306a66569693d57c26be0978da509bb3309af54328510fe9e",
             'normalized': "23f0f1f8b0ad47b306a66569693d57c26be0978da509bb3309af54328510fe9e",
             'sentences_normalized': [
                 "32ff6ad2a8810ca9d6ecaa531c5fed5fa2e0ac1af341d9ccac92e17a2ffb88a5",
                 "5432f96cbd7f33bb89ea33876adc82c2911953d4930e3e3dc23d67f98e18f74d",
                 "ef85d5b8a82782a716edecb6bfa028272f3381c365609fdb776732ec0fadf2bb",
                 "c719fa4e0cbd94e3b339c19d9ea080aa002efdb44a8d94db042e8acb827da8b2",
                 "3c742bdb62e92c82565e753139fb55b0f13230267832ef7f57092689a782aeb9",
                 "9890845acb572623f273211f0d4350e49f4edd593b68799c2bd216d758ddbe62",
                 "b849c0e7d8effb959a50816b69453835a7a011535850d489e442aa11e4c0c035",
                 "887c9d50adf168090cd90661e4bb72820713569cf8a88247ce4d966a1447d637",
                 "8fb066bf2a17244cf51d6ed0018c39802857165c3023bb8a0f936290e1dec069",
             ],
             'sentences_raw': [
                 "32ff6ad2a8810ca9d6ecaa531c5fed5fa2e0ac1af341d9ccac92e17a2ffb88a5",
                 "5432f96cbd7f33bb89ea33876adc82c2911953d4930e3e3dc23d67f98e18f74d",
                 "ef85d5b8a82782a716edecb6bfa028272f3381c365609fdb776732ec0fadf2bb",
                 "c719fa4e0cbd94e3b339c19d9ea080aa002efdb44a8d94db042e8acb827da8b2",
                 "3c742bdb62e92c82565e753139fb55b0f13230267832ef7f57092689a782aeb9",
                 "9890845acb572623f273211f0d4350e49f4edd593b68799c2bd216d758ddbe62",
                 "b849c0e7d8effb959a50816b69453835a7a011535850d489e442aa11e4c0c035",
                 "887c9d50adf168090cd90661e4bb72820713569cf8a88247ce4d966a1447d637",
                 "8fb066bf2a17244cf51d6ed0018c39802857165c3023bb8a0f936290e1dec069",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 263, 'begins': "And it is", 'ends': "wet and hot.",
             'raw': "6d44b3359a5bb5758c48834042ceb6e17ce2656d61575e74fdc9fb0aaa268bf8",
             'normalized': "6d44b3359a5bb5758c48834042ceb6e17ce2656d61575e74fdc9fb0aaa268bf8",
             'sentences_normalized': [
                 "fb27b90541d62a9486c73b470ede35b61f11e8df33ca352ee31a54405c805bd6",
                 "db82d982f7e5845c39886057fcb088e2b20cb24adc051b7735579e74cf19fa6c",
                 "f3abdee0d36472499bb101bbc23ecb705d0a0fe4a8811a0f09e342a112887795",
                 "2d4536656181dcbb79284b5b15264578cd551916879ef3706f277de19d230333",
                 "e14914a5132fa42f1908ff97283bb0bf66dd54bd05f8c2fb444039e70cbfb69c",
                 "4b70d30caffc2770b1f833717d6ad30f93a559d8da8593c80f77ec498b3e9002",
                 "fa42711e382b502dcbd42e5df6274a840e7a4759df9358918a65e949181a366a",
                 "4295c26c82e8ba1c420bb7fe19a9825b2f0c7843762920c356d473dbec6a1acb",
                 "cc1925f4bf73159e109dc255e66e173bfc90158bd4e364eb20be45de23db3a26",
                 "cd65a4350839e6956f0117314f5e80805fff343f3a11672476dea44012e50657",
                 "8cd5343d2f627ec6273e4d01591a444046e259c65b10c3359f4f4131517fcf55",
             ],
             'sentences_raw': [
                 "fb27b90541d62a9486c73b470ede35b61f11e8df33ca352ee31a54405c805bd6",
                 "db82d982f7e5845c39886057fcb088e2b20cb24adc051b7735579e74cf19fa6c",
                 "f3abdee0d36472499bb101bbc23ecb705d0a0fe4a8811a0f09e342a112887795",
                 "2d4536656181dcbb79284b5b15264578cd551916879ef3706f277de19d230333",
                 "e14914a5132fa42f1908ff97283bb0bf66dd54bd05f8c2fb444039e70cbfb69c",
                 "4b70d30caffc2770b1f833717d6ad30f93a559d8da8593c80f77ec498b3e9002",
                 "fa42711e382b502dcbd42e5df6274a840e7a4759df9358918a65e949181a366a",
                 "4295c26c82e8ba1c420bb7fe19a9825b2f0c7843762920c356d473dbec6a1acb",
                 "cc1925f4bf73159e109dc255e66e173bfc90158bd4e364eb20be45de23db3a26",
                 "cd65a4350839e6956f0117314f5e80805fff343f3a11672476dea44012e50657",
                 "8cd5343d2f627ec6273e4d01591a444046e259c65b10c3359f4f4131517fcf55",
             ]},
        ]},
    3: {'location': "I.6, 23,16–24,10 H.; I.545,14–547,4 K.",
        'greek': "09f6c338ee8ce61b729c1ae56deb7e2807b4b82eb6265177ad4bddce4423a8dc",
        'refs': [
            {'translator': "Johnston", 'words': 258, 'begins': "In these, the", 'ends': "it functions best.",
             'raw': "c19e19ed6bb09f269982f1c8288522362d15e8d69680a92ea55764a21089e2eb",
             'normalized': "fef33c3fec4a1c3a856eb76c85b9bd834038ec6b3d11d17d61da4bb945ca70cb",
             'sentences_normalized': [
                 "d26768749653201a85805e70f35ae5eb39001302bfeaffcbee3843dd4b9aba44",
                 "28764bdb7d8b3f833d0be553fd22c6e24dbfcccafb62505f191966bce1862cd6",
                 "33a14641733873996f0c6e79e7471dc488b7b75f3092afbe09719667d5d627ae",
                 "cb1e66b207ee59233aa71539acf499699ee16fbb80c89752f5e8a511f44690ca",
                 "b124fa9e1e5da0e2b74475a2b779577a1c730125f7eef7e702e2d9dd7a908107",
                 "1c34789f68a6668f80ff4f82d76cf296206c5ecbbfb42f3ecafd8716fb9c593f",
             ],
             'sentences_raw': [
                 "d26768749653201a85805e70f35ae5eb39001302bfeaffcbee3843dd4b9aba44",
                 "28764bdb7d8b3f833d0be553fd22c6e24dbfcccafb62505f191966bce1862cd6",
                 "33a14641733873996f0c6e79e7471dc488b7b75f3092afbe09719667d5d627ae",
                 "cb1e66b207ee59233aa71539acf499699ee16fbb80c89752f5e8a511f44690ca",
                 "4e460a336eb6ac0a1d152907e9bce0330d45bf33bc194756f9b356d0e2df6c2e",
                 "1c34789f68a6668f80ff4f82d76cf296206c5ecbbfb42f3ecafd8716fb9c593f",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 305, 'begins': "Of these, the", 'ends': "its activities optimally.",
             'raw': "79f20e25143249fe38d496a0da71057c3f7bdcff4445eb9f04ed9d25a8aaf902",
             'normalized': "d54aa040a80a6b0a09ddb3dc468393ba8f1d8706b492efd5f8f2e00e7ad1ebac",
             'sentences_normalized': [
                 "f6a4ac84ceefe5a616c4798f6d092d20b48a0c9e23e86784a6493855e85c2fcb",
                 "31de91023c3cd60ad52961da2c0618a2ccf98fabd98e9b4019498ff184019e68",
                 "c8408a32db46e93729169a2d3ce57750c44ead99d5e620959736d9874320dbf1",
                 "630f81f9bc264b2949e9dacd8be35869e2752b9c5173a302508b86f9e32e5054",
                 "fea7746dab72d45e32529d553c98ddbdc845da26dd00915e0418efdfc640df3a",
                 "d0177ba46bfb426a62cd21dc0aed47a4a55b1719f1a0fd66cd233ba2cf24e321",
                 "425edf39b655a41761290e6f4fe7295e239ab5af07033c0591f561fdac6157d2",
                 "92ccc67618031482ffb0671261675f5733bbb0846f8b0859fd3be2d7d4d3fc07",
             ],
             'sentences_raw': [
                 "f6a4ac84ceefe5a616c4798f6d092d20b48a0c9e23e86784a6493855e85c2fcb",
                 "31de91023c3cd60ad52961da2c0618a2ccf98fabd98e9b4019498ff184019e68",
                 "c8408a32db46e93729169a2d3ce57750c44ead99d5e620959736d9874320dbf1",
                 "630f81f9bc264b2949e9dacd8be35869e2752b9c5173a302508b86f9e32e5054",
                 "fea7746dab72d45e32529d553c98ddbdc845da26dd00915e0418efdfc640df3a",
                 "d0177ba46bfb426a62cd21dc0aed47a4a55b1719f1a0fd66cd233ba2cf24e321",
                 "ea47db5afe3aea876bf9fa66f7f958d262ed42273ab1277bcda056d465a04be7",
                 "92ccc67618031482ffb0671261675f5733bbb0846f8b0859fd3be2d7d4d3fc07",
             ]},
        ]},
    4: {'location': "I.9, 35,3–28 H.; I.564,7–565,14 K.",
        'greek': "f4ba1448095e817b9a903eb7b2df62fc5aa8456a96281f713c63e88386a6df45",
        'refs': [
            {'translator': "Johnston", 'words': 256, 'begins': "Therefore, those parts", 'ends': "appropriate to each.",
             'raw': "67931bef001c198b7f5a0493e025aafef23d8203c547e53e69e4885cede90ca4",
             'normalized': "ad8a2a79551cf12469584b156654a368f1a86ace8f8959ed0f88e9b6a1103aad",
             'sentences_normalized': [
                 "3373fe7bea7b1614219038fda540607fec4349cb6a11353a13673d47d59e3647",
                 "fa030948c94e2bf0a0e7e9d9763a95d2ca85cfe8a63cac768782737fb7aedc34",
                 "8b317f3ad45b2132d2fb15d7d942f35cb75887ee911e1144b32fe8964b0ca4b9",
                 "e060393c9c828098b8351d6749fa7b164ce15174bd8ae2bc75c7decec77fd878",
                 "16c6bd2ce3ba67deb127e04ff0ec5759a1e1fa63ebba0b63ee0dfe01d2be45ac",
                 "d32578c744112f5f5135784e866a426acebfe9ef0f8cae53c481b100ce5b7f22",
                 "e1e2dd7009fc1eb6594a915a7777f63187dc4739919ca971260847024ff5251a",
             ],
             'sentences_raw': [
                 "3373fe7bea7b1614219038fda540607fec4349cb6a11353a13673d47d59e3647",
                 "fa030948c94e2bf0a0e7e9d9763a95d2ca85cfe8a63cac768782737fb7aedc34",
                 "8b317f3ad45b2132d2fb15d7d942f35cb75887ee911e1144b32fe8964b0ca4b9",
                 "5e025b83243d0b01ffefb327ae1242689ac7bf115610f6d1fd896717349a4182",
                 "16c6bd2ce3ba67deb127e04ff0ec5759a1e1fa63ebba0b63ee0dfe01d2be45ac",
                 "d32578c744112f5f5135784e866a426acebfe9ef0f8cae53c481b100ce5b7f22",
                 "e1e2dd7009fc1eb6594a915a7777f63187dc4739919ca971260847024ff5251a",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 311, 'begins': "Now, those parts", 'ends': "appropriate to each.",
             'raw': "5f0a503432475742d2d3e374a2d0e8833f65fa49e6fa2e7e1815a6307e3d8dea",
             'normalized': "5f0a503432475742d2d3e374a2d0e8833f65fa49e6fa2e7e1815a6307e3d8dea",
             'sentences_normalized': [
                 "5fadbde5d159d9016e0b25a96cc9fad1ed8753548e8c4536a8a73f3c4f72463d",
                 "0e325e791ba4e2e48b110a7b6978229d82a75550f3c813986f8efc779ca3463d",
                 "9333a67782ba480857fe4287b8bfd782fc37be0ece05a99f35d66d30b6a771f0",
                 "b043d7d325d8deb9c6c69da8f4eb1078c0ea6a540a8c27d887c2814672adec39",
                 "59edb21b900e1975bea5bb33d9b8c4a7afbd158f2037d3dd0d2714192e05c916",
                 "c6db8cdfc8f3eef1fd63cb0feb13c248e202950a0ef049ea17b3670ac2d4c01f",
                 "699a2c03b39feacc27bb12fcb828e775310a002a86e90f92cde31cbc982d1a8f",
                 "ef181382ae10f14078a3194808c3877526725fc88b1d402f5d399673a1231be4",
             ],
             'sentences_raw': [
                 "5fadbde5d159d9016e0b25a96cc9fad1ed8753548e8c4536a8a73f3c4f72463d",
                 "0e325e791ba4e2e48b110a7b6978229d82a75550f3c813986f8efc779ca3463d",
                 "9333a67782ba480857fe4287b8bfd782fc37be0ece05a99f35d66d30b6a771f0",
                 "b043d7d325d8deb9c6c69da8f4eb1078c0ea6a540a8c27d887c2814672adec39",
                 "59edb21b900e1975bea5bb33d9b8c4a7afbd158f2037d3dd0d2714192e05c916",
                 "c6db8cdfc8f3eef1fd63cb0feb13c248e202950a0ef049ea17b3670ac2d4c01f",
                 "699a2c03b39feacc27bb12fcb828e775310a002a86e90f92cde31cbc982d1a8f",
                 "ef181382ae10f14078a3194808c3877526725fc88b1d402f5d399673a1231be4",
             ]},
        ]},
    5: {'location': "II.2, 47,22–48,16 H.; I.584,3–585,10 K.",
        'greek': "43c45cd84524641d910afad486e72f5ba021e59445f52a897aee0d1dc6a218f6",
        'refs': [
            {'translator': "Johnston", 'words': 302, 'begins': "In turn, from", 'ends': "in their prime.",
             'raw': "ab4680e3a356440f2d2c15247fbd0c7dff16eb1ef97b5976b6e4fc5e38e24a9b",
             'normalized': "6a48e78336a53c39c0c58083f7608381a4124019f0750f7c2a746037a98941be",
             'sentences_normalized': [
                 "02ec778eb42b36f853ce5f0a7e7a12b05bd24e804f787dfacce64796e567a8b1",
                 "d1f16008fea590bc0ce314c4cce0035a0c64e6769e9909d863a3396995fb4588",
                 "7db3ff83e084d371e9f195a8695ef6a1288716fe241f7228fa15e4a4ac9ed27c",
                 "c8f0317c962998ca3b6fb1d972652282ef36c8af70ebaeec4919a0255abbe6be",
                 "2eb5befdd69594d4165a1dc2175c7e14790ccded15b19f389bcdb4755bf28591",
                 "7786645389dce89b9eb2816d12b5af1fae8e5e0f6bfaf834753685c1635a5012",
                 "7ab39022df94c58d1f293fcff2f940f832fc5098c8dc1202edbe68178f0d9e81",
                 "dcff38348b7ae2c942cc060d52d7318c415fdd301d0ea45bc11f885c858619da",
                 "a5207ac1f496741d1e546b162323a554427d9b85d2eda6a656a9500d00a0c7e7",
                 "a63e3dda2097a1440c39fb965aa1b45977bd851100a85a2522257e9216994e5e",
                 "477d08a1da04d81267a20e52d63414775c65553a91db331812855414d39b92e7",
             ],
             'sentences_raw': [
                 "02ec778eb42b36f853ce5f0a7e7a12b05bd24e804f787dfacce64796e567a8b1",
                 "d1f16008fea590bc0ce314c4cce0035a0c64e6769e9909d863a3396995fb4588",
                 "7db3ff83e084d371e9f195a8695ef6a1288716fe241f7228fa15e4a4ac9ed27c",
                 "c8f0317c962998ca3b6fb1d972652282ef36c8af70ebaeec4919a0255abbe6be",
                 "2eb5befdd69594d4165a1dc2175c7e14790ccded15b19f389bcdb4755bf28591",
                 "7786645389dce89b9eb2816d12b5af1fae8e5e0f6bfaf834753685c1635a5012",
                 "57324198a1f36b8b4f173980601029b132f424c2b838cbf771e7d09616d1a9f4",
                 "dcff38348b7ae2c942cc060d52d7318c415fdd301d0ea45bc11f885c858619da",
                 "a5207ac1f496741d1e546b162323a554427d9b85d2eda6a656a9500d00a0c7e7",
                 "a63e3dda2097a1440c39fb965aa1b45977bd851100a85a2522257e9216994e5e",
                 "477d08a1da04d81267a20e52d63414775c65553a91db331812855414d39b92e7",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 302, 'begins': "Again, on the", 'ends': "in the prime.",
             'raw': "f177e3c672df0bcb7a52583261882dbbb2aa6d88b8cad8cfd8da3790ccc42eb6",
             'normalized': "5bd722613230c7d49d3354c4ea047724dac1adf0f20e0064fecb75ba7583ddb5",
             'sentences_normalized': [
                 "fdfb23fb1105350ae9b90d12bd61dafbe061b5f3604b362b6f0a8a1910c00a58",
                 "8ea392203380c1cec19e4600ab5bc5ce8a68dd98584e89c5aeb3cc3882a935f7",
                 "35fa010f0d3a4f18da3c19c42eb04e87a006f8269105c373c8d66237f96cd778",
                 "8e31006ac98a7710610a590e2fff3d9cba27f07198f8c263cf2e185babca331b",
                 "2948ada73ab75339621d8514887852b78a15b1d3a245ec083a674e3da37f2698",
                 "cb787708ba28cb19420357e41753f55c9383b326256145a9ae115f4996012251",
                 "fc1a056057ecd3e735b1aadbbe8871c0b99c66c45bf91757ec78e6213f5af0ac",
                 "a5c6830780242cf05b328125c32b26635187b963326c856e660535f02b134bb3",
             ],
             'sentences_raw': [
                 "fdfb23fb1105350ae9b90d12bd61dafbe061b5f3604b362b6f0a8a1910c00a58",
                 "8ea392203380c1cec19e4600ab5bc5ce8a68dd98584e89c5aeb3cc3882a935f7",
                 "35fa010f0d3a4f18da3c19c42eb04e87a006f8269105c373c8d66237f96cd778",
                 "8e31006ac98a7710610a590e2fff3d9cba27f07198f8c263cf2e185babca331b",
                 "f5a94ae5650be5fabd3a50745c222b4249d24d8f6bc31c5453b9e6bf4032f832",
                 "cb787708ba28cb19420357e41753f55c9383b326256145a9ae115f4996012251",
                 "fc1a056057ecd3e735b1aadbbe8871c0b99c66c45bf91757ec78e6213f5af0ac",
                 "a5c6830780242cf05b328125c32b26635187b963326c856e660535f02b134bb3",
             ]},
        ]},
    6: {'location': "II.3, 59,6–60,4 H.; I.602,11–604,1 K.",
        'greek': "bf07685c24b591d6ca3c95c39a53a591893f8b3d0245e096c8c3884c9c422c6b",
        'refs': [
            {'translator': "Johnston", 'words': 265, 'begins': "All membranes are", 'ends': "become like this.",
             'raw': "af8011db136e97ac2d828d709886e18b7cdba9ecbbf9c709dde4e69645a9ea91",
             'normalized': "3c496b90f9b3323a9def49ae7ac381f256e5c9f3d778fceff4d2281c918a57b1",
             'sentences_normalized': [
                 "7e9d28402cc53cc99813b0a41cb77829201654d1f4d080ef4d3732577a148f3c",
                 "b95886a4ce93f85c1b1aceaf151805e42ff2abc5f94c6e7b60bfdddfb49477a7",
                 "dbe29fd9f8de89af117b9a7828ee227ea6abdc42d9abd317242a10073a7e0bd3",
                 "6f492544a1425257c07c11fb10dd3b2e730f40936b9b799555c791ce631c5f96",
                 "ddbefa9118e3a82c54a15f382c3b622f7a37797ea9773869fdc17039b7c5ffba",
                 "ffa64fcbc1059c2395c3ebca8896d85ba540955778b562b28e64ac09b1431c2c",
                 "6ec224405eba175a2e22dde803459839be0cec8d10160382546700ef39e4e49f",
                 "5d7abb9bf8eb75ad8fb03f148c25d9f75d9103abf5a08e862a50ab12c9496687",
                 "ac01eefd4395e98573d7256c3b7f862c3a1ed7ac11946c3b68f889836bfe92ea",
                 "9e3a6c6350dcf99ec8aef23ecbe109c3dd53ccc7b4d09f2727c31b0ed811066a",
                 "76c27ba1c8a45e7647ff9c3bc2a8ab53c08b01fc2e71c56c1299a5f7b178f2b2",
             ],
             'sentences_raw': [
                 "7e9d28402cc53cc99813b0a41cb77829201654d1f4d080ef4d3732577a148f3c",
                 "b95886a4ce93f85c1b1aceaf151805e42ff2abc5f94c6e7b60bfdddfb49477a7",
                 "902e59981dc88302e67a84798fcfc71a484c49e7f5a2ffb1c8ffe012b95f50b4",
                 "6f492544a1425257c07c11fb10dd3b2e730f40936b9b799555c791ce631c5f96",
                 "ddbefa9118e3a82c54a15f382c3b622f7a37797ea9773869fdc17039b7c5ffba",
                 "ffa64fcbc1059c2395c3ebca8896d85ba540955778b562b28e64ac09b1431c2c",
                 "6ec224405eba175a2e22dde803459839be0cec8d10160382546700ef39e4e49f",
                 "5d7abb9bf8eb75ad8fb03f148c25d9f75d9103abf5a08e862a50ab12c9496687",
                 "ac01eefd4395e98573d7256c3b7f862c3a1ed7ac11946c3b68f889836bfe92ea",
                 "9e3a6c6350dcf99ec8aef23ecbe109c3dd53ccc7b4d09f2727c31b0ed811066a",
                 "76c27ba1c8a45e7647ff9c3bc2a8ab53c08b01fc2e71c56c1299a5f7b178f2b2",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 290, 'begins': "All membranes, certainly,", 'ends': "has become so.",
             'raw': "d3e6916a6deacbdb16415e7a103661e52e51d48962a6629b9b9aa5f6639df7d9",
             'normalized': "97a96ab92e17fc2eabc0107a5bac43047ad05b283b517a8e539c2539b257af04",
             'sentences_normalized': [
                 "72484427df4e1124cc3c5047a8f69d3bfbdda137f7d62eda8ada522c621d0381",
                 "4fef119619b857cce382f28c9ad93774de94a4f9187670dcc9768d207fe72ff2",
                 "412a53cfbc1e7a70b737206517c6133ff62acd4fc29ea2eb4d2c5e489e508a2d",
                 "5b7409321ed934a8e43b48026680c5cfccdf3250e75ef095b8c542096780689e",
                 "cc150247cf5068f987c7a7931c3ef3b659c1520260b3a15f62bf4b3653a56e15",
                 "905075b5606a1207fdffcdb7f3614d28b86a2b38357f5b501028822fb3a2457a",
                 "d05bedc1960b4aa24d2a97cbc3471644e93a50099c94d50845c2b5d57dfcb70f",
                 "f51441e150ccdce451ed95318a82618c304fe15252131a56f82ef1b194f769fd",
                 "978ddbadbc38ec113153bf020c108ab0b875d7bd85c0f8cf0c5c32fc3356bbd6",
                 "15c0e87ff561b60f5483b8077e416fb5a2dc798b5320b23985f7fc7e425e275c",
                 "89d47aa3c52c2dda0bcb36d0af557fb19a996a27b7a5d376024dc82e2704a6c0",
             ],
             'sentences_raw': [
                 "72484427df4e1124cc3c5047a8f69d3bfbdda137f7d62eda8ada522c621d0381",
                 "4fef119619b857cce382f28c9ad93774de94a4f9187670dcc9768d207fe72ff2",
                 "412a53cfbc1e7a70b737206517c6133ff62acd4fc29ea2eb4d2c5e489e508a2d",
                 "1050ac6b682539c386b3a560baa4500bebcbed020abf59b8b2227be1c8896905",
                 "cc150247cf5068f987c7a7931c3ef3b659c1520260b3a15f62bf4b3653a56e15",
                 "905075b5606a1207fdffcdb7f3614d28b86a2b38357f5b501028822fb3a2457a",
                 "d05bedc1960b4aa24d2a97cbc3471644e93a50099c94d50845c2b5d57dfcb70f",
                 "f51441e150ccdce451ed95318a82618c304fe15252131a56f82ef1b194f769fd",
                 "978ddbadbc38ec113153bf020c108ab0b875d7bd85c0f8cf0c5c32fc3356bbd6",
                 "15c0e87ff561b60f5483b8077e416fb5a2dc798b5320b23985f7fc7e425e275c",
                 "89d47aa3c52c2dda0bcb36d0af557fb19a996a27b7a5d376024dc82e2704a6c0",
             ]},
        ]},
    7: {'location': "II.5–6, 70,6–71,5 H.; I.620,13–622,5 K.",
        'greek': "356eaf4e745764101868eb184faed2fc0046cb1adb327ee00dbc3ea78ea10832",
        'refs': [
            {'translator': "Johnston", 'words': 294, 'begins': "For it was", 'ends': "the whole body.",
             'raw': "1c92b903b7e6156180875d80a59b1c558e231807c99221597ee71c56e8bd98c8",
             'normalized': "1c92b903b7e6156180875d80a59b1c558e231807c99221597ee71c56e8bd98c8",
             'sentences_normalized': [
                 "9874dfa86432077ba21855cbd84ddbe91cb6c8cb44272f53518e90b112ddf076",
                 "8c4d7154735e9a3849818d50640dca3209f3e8fa05e990b2fad8269270439d08",
                 "fafd20dc1324b49cd5d3ac6d9f6c31275a8ffdd169a4da5c840409fccb8b29a2",
                 "ead4f665952712f263510c05d1d0423a8f51f7ff4b88a35a32e1b3dfcc078225",
                 "75a6a6c5f1c13250b012ea72d4457e5bccd5026f888d53fbfdd48b3e74d377d7",
                 "2d6fe5e5e1ae0ce76f02c3058dffeaab2774c35b91f4ba21e969342434920fe3",
                 "61214d956052b2334079e710774dd16832de3aef007e2c0304fbd3bffce81ca3",
                 "7b86bdaf7f612cb90762c1cc8aabf56f8141ef27c27217138412c74aff810d51",
                 "103ed46192b5f4cd787256227ca3c4b0b1fb191a52826353b234fa2b092816f2",
             ],
             'sentences_raw': [
                 "9874dfa86432077ba21855cbd84ddbe91cb6c8cb44272f53518e90b112ddf076",
                 "8c4d7154735e9a3849818d50640dca3209f3e8fa05e990b2fad8269270439d08",
                 "fafd20dc1324b49cd5d3ac6d9f6c31275a8ffdd169a4da5c840409fccb8b29a2",
                 "ead4f665952712f263510c05d1d0423a8f51f7ff4b88a35a32e1b3dfcc078225",
                 "75a6a6c5f1c13250b012ea72d4457e5bccd5026f888d53fbfdd48b3e74d377d7",
                 "2d6fe5e5e1ae0ce76f02c3058dffeaab2774c35b91f4ba21e969342434920fe3",
                 "61214d956052b2334079e710774dd16832de3aef007e2c0304fbd3bffce81ca3",
                 "7b86bdaf7f612cb90762c1cc8aabf56f8141ef27c27217138412c74aff810d51",
                 "103ed46192b5f4cd787256227ca3c4b0b1fb191a52826353b234fa2b092816f2",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 303, 'begins': "(For it was", 'ends': "as a whole.",
             'raw': "096ec4f556d47dd1d33761ec460802c1de34fa140d51ed284b819e785e7d05b1",
             'normalized': "b0b0fd945fe0dd0e05a1857c2c89db7e6e263e9374e506620652c9da01115270",
             'sentences_normalized': [
                 "69d7d4cb97796d36d5bfaf04c20c411986f9f9d429fc026febc0c165fb509893",
                 "755414e73d4119aaeaea6bf0899aa8c37943f1e8124b8a7e2e9a6749c3fb1a8e",
                 "8a72882dbb51291f1698321d08935cfcd7c17b4ae58a55d001e9979a8d8d9adb",
                 "4c5a8fd387d2f2af8165df9a84a7480326e2edcaacea5ba79c02da154defa664",
                 "35a9d6f04fb20a93c64b8d9cecddb4c38bf8b244225e8c09b3b7ba5f6cc38257",
                 "c6192d7f3e98460df551a204a261e2dc693bb4582a5d36ec5dd6ff3c6c05c316",
                 "ccc4ecf4de40f66554ea8412011fc38613fbe7d470071872eae88c2d93217d9b",
             ],
             'sentences_raw': [
                 "69d7d4cb97796d36d5bfaf04c20c411986f9f9d429fc026febc0c165fb509893",
                 "755414e73d4119aaeaea6bf0899aa8c37943f1e8124b8a7e2e9a6749c3fb1a8e",
                 "fd77c5fd5b00a4ff126b834fcd9a70180e2d30b0ede5f387bc6537effc7ec321",
                 "4c5a8fd387d2f2af8165df9a84a7480326e2edcaacea5ba79c02da154defa664",
                 "35a9d6f04fb20a93c64b8d9cecddb4c38bf8b244225e8c09b3b7ba5f6cc38257",
                 "c6192d7f3e98460df551a204a261e2dc693bb4582a5d36ec5dd6ff3c6c05c316",
                 "ccc4ecf4de40f66554ea8412011fc38613fbe7d470071872eae88c2d93217d9b",
             ]},
        ]},
    8: {'location': "II.6, 81,10–82,3 H.; I.638,11–639,16 K.",
        'greek': "abc9ff223018e9622698f941764c60e643470e5c21b6574eaf4fafc24355f637",
        'refs': [
            {'translator': "Johnston", 'words': 274, 'begins': "And those in", 'ends': "krasis is wet.",
             'raw': "dec56a5e9c0d8757a020762edc8843420a3e2177bb7b218c8a3ecb01eef37f3e",
             'normalized': "dec56a5e9c0d8757a020762edc8843420a3e2177bb7b218c8a3ecb01eef37f3e",
             'sentences_normalized': [
                 "ab68fbed6023f50f0d9b601caa82dfe1aeea19db97d38003b7afda33183459b9",
                 "9ea7533faaa8d648c35309483ea59cf304d8ca7e9865aaf65ec14762f9e82745",
                 "ae669b90a351caec6524ecec73db90ce851434551f41afe404ae194cc07e769a",
                 "56ff98e759c9d344af62f9268b0a0f25b59c529c778e26583bb8142a4e6cc15b",
                 "3e11ed90b3b277de2ef80eac3c9b9959ececc899ca201578aae922a2a3600808",
                 "9990039ba7f5fe72a6098e68899ec72ad94c92786511946f7aaf99c10f5672ab",
                 "370a28e9c16d38a0717bbd50facc7bc7aea896e090c61e6e7e109f3a6d2c70b2",
                 "7be1b82cebcfc2bc1b53e65098cdf8fc93402964687e31436e3d672202d8acdd",
                 "f71ea20107d648d4287c09503bbbf2f040ba77f71529a0ca57fd0d6218047717",
                 "009d348d52f300ad5459d18e2ce176bbd7f73c40f9999291e8c2c693b7515b44",
                 "84a880401558291a2bd4b7d9f69229c27fab7732ba45e7dd5ac22d9b4d1b44c6",
                 "4326105649c3024cb045ab80f43ff3cf4695f0b4ecc3e48e2f71c2fa6331048b",
             ],
             'sentences_raw': [
                 "ab68fbed6023f50f0d9b601caa82dfe1aeea19db97d38003b7afda33183459b9",
                 "9ea7533faaa8d648c35309483ea59cf304d8ca7e9865aaf65ec14762f9e82745",
                 "ae669b90a351caec6524ecec73db90ce851434551f41afe404ae194cc07e769a",
                 "56ff98e759c9d344af62f9268b0a0f25b59c529c778e26583bb8142a4e6cc15b",
                 "3e11ed90b3b277de2ef80eac3c9b9959ececc899ca201578aae922a2a3600808",
                 "9990039ba7f5fe72a6098e68899ec72ad94c92786511946f7aaf99c10f5672ab",
                 "370a28e9c16d38a0717bbd50facc7bc7aea896e090c61e6e7e109f3a6d2c70b2",
                 "7be1b82cebcfc2bc1b53e65098cdf8fc93402964687e31436e3d672202d8acdd",
                 "f71ea20107d648d4287c09503bbbf2f040ba77f71529a0ca57fd0d6218047717",
                 "009d348d52f300ad5459d18e2ce176bbd7f73c40f9999291e8c2c693b7515b44",
                 "84a880401558291a2bd4b7d9f69229c27fab7732ba45e7dd5ac22d9b4d1b44c6",
                 "4326105649c3024cb045ab80f43ff3cf4695f0b4ecc3e48e2f71c2fa6331048b",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 277, 'begins': "Then, too, a", 'ends': "wet overall mixture.",
             'raw': "c589b8c0548e999e70691535ddedb01c7c47bd09ccd1f6c7cef769282c23bc57",
             'normalized': "65f1fdac45c30bab70d10448d6993d5086f21f069a2f7aed44645813a468a1d2",
             'sentences_normalized': [
                 "8946fe2a05b329fe856a8c8b66a3d83ac2ef861dc087ef6ea6e658d11e361aa4",
                 "fb2fd4b1746facbafd9d4e3a48dc0d59e229ae287825ab4fc82e7976584724e5",
                 "69956e60dae5320060d3bb92f2956183d1c7ad13a1b312c56d0bde7a90bdc324",
                 "daff6feeca4974c3136eedf8842f7f95b739b15abb1e16264891509fba28553b",
                 "b516e12de2bb67b302a3d1a9c3995c767b9a5b995a87b69a145eb31cb27d22ff",
                 "46805025dbb6d13188691438657da6d799b5a6b8bfb670a62f5ff441d94ad64e",
                 "e167ba5ba80df45b5c80df9182b043f075261a0c5373c748c6be0a9fbd597cef",
                 "6e1a35c70d5903b81ba348cec25c1d26136f0959b072305ccae4b2cd84df5dec",
                 "093ab808fb650b1a39a48c95c0e5ec920abb113cd55313959a8a4428ddca8d4e",
             ],
             'sentences_raw': [
                 "8946fe2a05b329fe856a8c8b66a3d83ac2ef861dc087ef6ea6e658d11e361aa4",
                 "fb2fd4b1746facbafd9d4e3a48dc0d59e229ae287825ab4fc82e7976584724e5",
                 "2d26d3e9dbcc5617eb7158b23a5d666438a08e9a0ba88a4731b60e8a29e53504",
                 "daff6feeca4974c3136eedf8842f7f95b739b15abb1e16264891509fba28553b",
                 "b516e12de2bb67b302a3d1a9c3995c767b9a5b995a87b69a145eb31cb27d22ff",
                 "46805025dbb6d13188691438657da6d799b5a6b8bfb670a62f5ff441d94ad64e",
                 "e167ba5ba80df45b5c80df9182b043f075261a0c5373c748c6be0a9fbd597cef",
                 "61d6402a50488760736a5de94a4f9204b4d9e2199aefdbc110be3fd3703da4e0",
                 "093ab808fb650b1a39a48c95c0e5ec920abb113cd55313959a8a4428ddca8d4e",
             ]},
        ]},
    9: {'location': "III.2, 93,21–94,21 H.; I.658,5–659,13 K.",
        'greek': "05ce350ead3ab44e29bb3eedc11487a2a5ac0a52640d06ed2d22bc2e8611d1fd",
        'refs': [
            {'translator': "Johnston", 'words': 303, 'begins': "And the medication", 'ends': "leading to extinction.",
             'raw': "6fdeb6bbd4fc65deadf7dd779c5994a78ad0a227c80a2f7a30a6d714b481cabd",
             'normalized': "09b293a1a16c0ec0162b77a31a13225f5cf7c7f91d15149e597f87e9d8f941f4",
             'sentences_normalized': [
                 "72f9f5b40e284b8f8d4d93738d0950479fcee586b78084d28593cfb7c550ffae",
                 "e7b4740855a96584dc8534fa6516117fb172a5058f8cb6047dfe9fe035e5a056",
                 "728d5f88e380f9bf3ea978ac30121bf2e3398823c591e37df7643387d5e94a23",
                 "f65aeeeb20b04d79ae05b9995f69e89f0c25902700edaf10fa36eba78f2b4856",
                 "6785f6bd0d62ce2416c43eb55f942c10aea306b055c5562e8daa300a9dbe4df4",
                 "045d44a68b0d3092bcc5dd8f7964ba91e5d783e17b2ae2b2f050c96d02d054c7",
                 "b4360e28bd1f5a9a309d2ac24f2c3c5441daa5ee1c36fc00b3eff068c9ad4f46",
                 "f4546deded28e825458427fb3a0f277ca523a287a0002580047368eed73c0b9f",
                 "f3fe235ebb66ab08f383ea10a66c4902fbb3d9c62d1302f51bc1b25344d7c212",
                 "ef1906556b1f2274d72ce67f2a1e3162227fbafc8a74d0437254227d030d71a9",
                 "e02381927244499fc576f8f795801b5a41718644839fb9787f3d34a4246884bd",
                 "cc3c0c54f4ebb7daae29c45d73d3ce4ee151d7f5b71334d27e0c709b82dc6f99",
             ],
             'sentences_raw': [
                 "72f9f5b40e284b8f8d4d93738d0950479fcee586b78084d28593cfb7c550ffae",
                 "e7b4740855a96584dc8534fa6516117fb172a5058f8cb6047dfe9fe035e5a056",
                 "728d5f88e380f9bf3ea978ac30121bf2e3398823c591e37df7643387d5e94a23",
                 "f65aeeeb20b04d79ae05b9995f69e89f0c25902700edaf10fa36eba78f2b4856",
                 "6785f6bd0d62ce2416c43eb55f942c10aea306b055c5562e8daa300a9dbe4df4",
                 "045d44a68b0d3092bcc5dd8f7964ba91e5d783e17b2ae2b2f050c96d02d054c7",
                 "b4360e28bd1f5a9a309d2ac24f2c3c5441daa5ee1c36fc00b3eff068c9ad4f46",
                 "f2ab908b850f093696d9152a56b993ed4d4c9c47ef5f387b308f1587711b5f8f",
                 "f3fe235ebb66ab08f383ea10a66c4902fbb3d9c62d1302f51bc1b25344d7c212",
                 "ef1906556b1f2274d72ce67f2a1e3162227fbafc8a74d0437254227d030d71a9",
                 "e02381927244499fc576f8f795801b5a41718644839fb9787f3d34a4246884bd",
                 "cc3c0c54f4ebb7daae29c45d73d3ce4ee151d7f5b71334d27e0c709b82dc6f99",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 304, 'begins': "Medea’s drug was", 'ends': "risk destroying it.",
             'raw': "f7c7bbd13b87a37673fbeab51a1197b73239bd44d7cf66c4c3d14d84fdd1160a",
             'normalized': "d2286e366d699f05adf9faea24000475273b0e50ad81382b3937317c33ce393d",
             'sentences_normalized': [
                 "16ed0de252071bc46788d897a34d832d6fe3c41e66368fe46b007738e33ebece",
                 "21f87fc8876bb857e0ffce90875c0276954ca441b494d3edffc11a82beae1106",
                 "01e4bcd0e11209963873ba9c71ccc070236db5595120e7647d30376c8e35d959",
                 "26f15b56e0ad3a82d4da63272b99c9c5ff0ed980715ea1f2643e5cfc43e4719f",
                 "2ef5cba1b092a6d878877e4914f009d030313d3983a6b06542ff93d249fe3f19",
                 "e2f0259442d05059c0f940c52a638e46eba8a2cc793c795106fc8bec68282371",
                 "ad07de25e2e0980c7db0b881808c29710ce4d5681957bd06e020545d3d8c58db",
                 "66e0e9b4e867064fa17305500422758df216f899f40f159a8c77b4461535e48c",
                 "2e6101fbd8a061bfb1702b4149be5fbc429a42120249f6003930bd989098ec93",
                 "e7ece711d9ba2fa4b7344a47113f6ce6c286d3e19a589dd8f4cee36751ecde08",
                 "0d9337df21ef1c22a00fe6b730470b4c5cfb093bdd2fb8d4a7234cb3b0db00f4",
             ],
             'sentences_raw': [
                 "08397230f1e929974672a3e33544bc2d4f4cd01d8912b2e27a77f26d98604222",
                 "21f87fc8876bb857e0ffce90875c0276954ca441b494d3edffc11a82beae1106",
                 "01e4bcd0e11209963873ba9c71ccc070236db5595120e7647d30376c8e35d959",
                 "26f15b56e0ad3a82d4da63272b99c9c5ff0ed980715ea1f2643e5cfc43e4719f",
                 "2ef5cba1b092a6d878877e4914f009d030313d3983a6b06542ff93d249fe3f19",
                 "31fa2c3a4a10721120a7433cc9f16e1407a55693966330a40bec63f93924b6d2",
                 "ad07de25e2e0980c7db0b881808c29710ce4d5681957bd06e020545d3d8c58db",
                 "66e0e9b4e867064fa17305500422758df216f899f40f159a8c77b4461535e48c",
                 "2e6101fbd8a061bfb1702b4149be5fbc429a42120249f6003930bd989098ec93",
                 "e7ece711d9ba2fa4b7344a47113f6ce6c286d3e19a589dd8f4cee36751ecde08",
                 "0d9337df21ef1c22a00fe6b730470b4c5cfb093bdd2fb8d4a7234cb3b0db00f4",
             ]},
        ]},
    10: {'location': "III.4, 105,2–27 H.; I.676,17–678,9 K.",
        'greek': "88f532404e65840f9889e0f2f74127b27a458b7b341a20cbaf59473a012af074",
        'refs': [
            {'translator': "Johnston", 'words': 310, 'begins': "For in this", 'ends': "of green wood.",
             'raw': "0205d13988fcd740e92d433de522ba4e93fe8ce0f3f936f12ecea2050eb4aec5",
             'normalized': "9eefd105ee098a059aa940508d71b6a481360c7a0b377cb83585713d1b82374b",
             'sentences_normalized': [
                 "75b07fac97b383b9c44246e7534dad1a35dccf81ed22a608ee7b77be2c836322",
                 "0c46fe2999051483a5d2ed8036698469146a2ec0a080d9769be6fce80077f7a6",
                 "145785d650fd1a2c33ee8dc930d7c9e1b0ca5a50a5bfb0ad48d91ce876949572",
                 "9b9d1764718bbefb2bec626e0f7659275ff5e8485427875395c080232dd040b2",
                 "c42933c57284f3406c02197e506f1041cae674c587259ecde2980e158fee4e2a",
                 "4a0958ec5a6d9d33bc3df9c233a99ad015b65faef349f9161b06b5006f562ac0",
                 "11102ba76d6e7e8b21c8a2942e5fe7929e0493befe3f15ca158bdb99c8e68fa2",
                 "2c1e193337612ed8d4b9bb0d14489f1cc3ef254398202ce332fafc61a8472696",
                 "72d2916b1b4c55c0eb7c6373bbc9d081fcb57103c76e55f01ea33166c8512afe",
             ],
             'sentences_raw': [
                 "75b07fac97b383b9c44246e7534dad1a35dccf81ed22a608ee7b77be2c836322",
                 "e41f92728d6585021bde06726ccdf1bc9144a36c1e5e5297ec182d4342e3495d",
                 "145785d650fd1a2c33ee8dc930d7c9e1b0ca5a50a5bfb0ad48d91ce876949572",
                 "9b9d1764718bbefb2bec626e0f7659275ff5e8485427875395c080232dd040b2",
                 "c42933c57284f3406c02197e506f1041cae674c587259ecde2980e158fee4e2a",
                 "4a0958ec5a6d9d33bc3df9c233a99ad015b65faef349f9161b06b5006f562ac0",
                 "11102ba76d6e7e8b21c8a2942e5fe7929e0493befe3f15ca158bdb99c8e68fa2",
                 "2c1e193337612ed8d4b9bb0d14489f1cc3ef254398202ce332fafc61a8472696",
                 "72d2916b1b4c55c0eb7c6373bbc9d081fcb57103c76e55f01ea33166c8512afe",
             ]},
            {'translator': "Singer & van der Eijk", 'words': 303, 'begins': "For if we", 'ends': "of green wood.",
             'raw': "67fb2bcb611729753885e270a7cc3f786ef6b5edb29612909537b5534aded3ed",
             'normalized': "67fb2bcb611729753885e270a7cc3f786ef6b5edb29612909537b5534aded3ed",
             'sentences_normalized': [
                 "00b04404b5fe5133fdf51b02c200b0915f09342689fc2841655e284d99bbab6f",
                 "ea200c18bb23f51d50816613296d6e9c77544e35d1a7544e8f2feae2fe939028",
                 "2b80376660f7087c68a36883d287b2f96ac28e056a0f701104084e082cfdfb1f",
                 "6d674a3c5f44c0f335dc5364d818678c61af9c8ecf58248961b395a24cc8f107",
                 "7047280c444a97d810005d150c1f1a02c76095e938775e91f78e2221d31f148d",
                 "931d868ceeca1c3c700cab662d39855ce4a8360d3830dd83a63a017231876c79",
                 "135a23e687e8d1f28cf3b7007453dc118e30115ee5eafb38a171cb7886f69064",
                 "dc43200b42bbb963cc8c7e34ec8846d18e948686c919293a0a73bdea12fb0d54",
                 "84ce9f6a8ad6e2a2bfd825a690864e7d9c5872d795ea56499880d425b9db7174",
             ],
             'sentences_raw': [
                 "00b04404b5fe5133fdf51b02c200b0915f09342689fc2841655e284d99bbab6f",
                 "ea200c18bb23f51d50816613296d6e9c77544e35d1a7544e8f2feae2fe939028",
                 "2b80376660f7087c68a36883d287b2f96ac28e056a0f701104084e082cfdfb1f",
                 "6d674a3c5f44c0f335dc5364d818678c61af9c8ecf58248961b395a24cc8f107",
                 "7047280c444a97d810005d150c1f1a02c76095e938775e91f78e2221d31f148d",
                 "931d868ceeca1c3c700cab662d39855ce4a8360d3830dd83a63a017231876c79",
                 "135a23e687e8d1f28cf3b7007453dc118e30115ee5eafb38a171cb7886f69064",
                 "dc43200b42bbb963cc8c7e34ec8846d18e948686c919293a0a73bdea12fb0d54",
                 "84ce9f6a8ad6e2a2bfd825a690864e7d9c5872d795ea56499880d425b9db7174",
             ]},
        ]},
}
COMP = {
    1: {'location': "I.2, XIII.367,10–369,1 K.",
        'greek': "3af97ecfb6ff1bd7ed4ae677580467b4f04174895e762a75167adcff7fadc570",
        'refs': [
            {'translator': "Marai", 'words': 292, 'begins': "Regarding the properties", 'ends': "point of burning.",
             'raw': "2858cdb243a3f77e9b0d19a99045724149282fe23ba063dec1afc11f53b14b68",
             'normalized': "83e1e68f1ff89e1ac6f4a5d948bbd82a7a262b6276fe108f7355e032fbd5d7f6",
             'sentences_normalized': [
                 "a55670c657913f114a9ae28e06143561c2a159e25e281a933864fa533e04c015",
                 "0ee590b06a63476934c2dbc66f1b8d7751e29ffff05100a89944c1d63ea1ff83",
                 "b3b5292e81e3c8e7e6653311f0e6dc5a7b143952256ec4ecd703442cc9e53d39",
                 "222f4d66670d6c01d20f2f2b9426f22ebf520c873342ef299238c9f3cce0ebfc",
                 "2ac9af6d307cb78210a152d6b3df8ca9b5c629e7f287c3e3b7d00c5298802938",
                 "8aab13927ac62c2f83675ca76eef47920697da49558d7782c79c8190b8a474b4",
                 "575288210d4707d6311e1632afc5a0df6cc456ec40632c200d257d718c645497",
                 "cdbfd109c32bb7c6bc84d76279c6979248e6486621ff4c0ac460872a1633cd67",
                 "9616d0f3d8485766424858fb28a267ca4a41812f7e5e44bd83d7a4a3d684710b",
             ],
             'sentences_raw': [
                 "fe5d08508db14a4e84f9fa0c53995d588931cb13eb59a0bbde663a8f40dfa1c9",
                 "0ee590b06a63476934c2dbc66f1b8d7751e29ffff05100a89944c1d63ea1ff83",
                 "b3b5292e81e3c8e7e6653311f0e6dc5a7b143952256ec4ecd703442cc9e53d39",
                 "222f4d66670d6c01d20f2f2b9426f22ebf520c873342ef299238c9f3cce0ebfc",
                 "2ac9af6d307cb78210a152d6b3df8ca9b5c629e7f287c3e3b7d00c5298802938",
                 "8aab13927ac62c2f83675ca76eef47920697da49558d7782c79c8190b8a474b4",
                 "575288210d4707d6311e1632afc5a0df6cc456ec40632c200d257d718c645497",
                 "cdbfd109c32bb7c6bc84d76279c6979248e6486621ff4c0ac460872a1633cd67",
                 "9616d0f3d8485766424858fb28a267ca4a41812f7e5e44bd83d7a4a3d684710b",
             ]},
        ]},
    2: {'location': "I.15–16, XIII.431,4–432,13 K.",
        'greek': "5d216c2d0d0dec7ad9757ad0dbb50c0fc1860c7338549ba1b3eb72e56b50b52d",
        'refs': [
            {'translator': "Marai", 'words': 315, 'begins': "However, nobody would", 'ends': "marrow, 2 unciae.",
             'raw': "8521640e88ae08cd59972daa9ae2bb38c326e1f427dad3b0b889c0be73c95613",
             'normalized': "7d28e5effa5a16ebea46208edd614b7f23a5159e4a2376301277c079922ab391",
             'sentences_normalized': [
                 "28c6bf6dc4037a187787b19c99baf147bdeace2e844a3da5a16da6af4675b9b1",
                 "868981aba762354a452333ed61b7bc2ed1b95cd90cba9764dad764705ae325ff",
                 "4ab6ad78ffd37ed12d19bcf2a4470a76da0e9e6dd64ec57c4a796f144cba56a7",
                 "06ba30e50f0a531c5442440caf45e9569ae3f734b059e12ab16519278cafeff1",
                 "a70c1b8f414697f485c9f2b3f4729821f193afaefd9ad32396ff4a3d3c6d97b1",
                 "3ec1d1e80d46e73bc4cdd8ffbefd465585ac8d88692825c5572babb285e8c436",
                 "3ce5e01019d6bb4eef8ee1e253f726c99faa5021a054eb986cb82973a1142c8e",
                 "5c9533232bb7978bd4dba4a603c4d33b68246e02703917b12f34e2c6b5ae38c9",
                 "a650c081a13e83e22051aa7e9d4e6e5a8f8ad430c67e60bb0afd87cd2b72ed86",
                 "b027d2d1ab8d8ba378f535770d58016c0ef4347933c0f9a0f49211799c94fd64",
                 "3a4208d989619fc9bd6d106a681b04969f141e1056f52bf98c8ebd148d805f99",
                 "5509534c8ca78a64fbce353d825b2eab94cbe5005fc9821ca34ea6b67758f170",
                 "91134e2443a8de8996478cf404bc638c046249ee8616a7499393aeef440806f0",
                 "4046626389a828ecadcaa7b2d90ca0722d81fd44eedc5845960c0bcc8bebf492",
                 "31449567b2f70b25e8918b0ed4168fe733304e79ea17b69a283dc29c8a933bcf",
                 "195b98a8ae1a7a7379c3145b5dd1a1b368ffeb86ba4e1519922ebe8de4766489",
                 "d89558b4867c7fde6bf5cb1ba7cfc3402aa8a72c5e747141a4255a2be5f23716",
                 "b341cf5a4845f39392c8ec3b6834f03d4594d7e4f40292051facf83fc6dc44b1",
                 "6ce49ba2b2548ec35968b740706f8994f7237870cd0a0ab29ad00bc6f631032b",
                 "5c4020dc2d7b6c0be3918883fac992d606f52303d26cebb140411bbad46311bb",
                 "3bcafa7d4afd7b3ff8d7d309dbdec88441ca5e0e0466cc6477cee52125729553",
                 "02e6cdfe9ba397c2dc534734a0b937f89777eb5a3f5b8f0162644a55a0a4585c",
                 "4ea137e2c7d57d0d166a04deb55fe0e30c94b1ce0248d0f8c800d6a284d070a8",
             ],
             'sentences_raw': [
                 "28c6bf6dc4037a187787b19c99baf147bdeace2e844a3da5a16da6af4675b9b1",
                 "868981aba762354a452333ed61b7bc2ed1b95cd90cba9764dad764705ae325ff",
                 "4ab6ad78ffd37ed12d19bcf2a4470a76da0e9e6dd64ec57c4a796f144cba56a7",
                 "06ba30e50f0a531c5442440caf45e9569ae3f734b059e12ab16519278cafeff1",
                 "a70c1b8f414697f485c9f2b3f4729821f193afaefd9ad32396ff4a3d3c6d97b1",
                 "3ec1d1e80d46e73bc4cdd8ffbefd465585ac8d88692825c5572babb285e8c436",
                 "3ce5e01019d6bb4eef8ee1e253f726c99faa5021a054eb986cb82973a1142c8e",
                 "4a2e0b4240ca1babb5b29ba8c0c035192c8c07f7c27f430397346cca7a43f423",
                 "a650c081a13e83e22051aa7e9d4e6e5a8f8ad430c67e60bb0afd87cd2b72ed86",
                 "b027d2d1ab8d8ba378f535770d58016c0ef4347933c0f9a0f49211799c94fd64",
                 "3a4208d989619fc9bd6d106a681b04969f141e1056f52bf98c8ebd148d805f99",
                 "5509534c8ca78a64fbce353d825b2eab94cbe5005fc9821ca34ea6b67758f170",
                 "91134e2443a8de8996478cf404bc638c046249ee8616a7499393aeef440806f0",
                 "4046626389a828ecadcaa7b2d90ca0722d81fd44eedc5845960c0bcc8bebf492",
                 "31449567b2f70b25e8918b0ed4168fe733304e79ea17b69a283dc29c8a933bcf",
                 "195b98a8ae1a7a7379c3145b5dd1a1b368ffeb86ba4e1519922ebe8de4766489",
                 "d89558b4867c7fde6bf5cb1ba7cfc3402aa8a72c5e747141a4255a2be5f23716",
                 "b341cf5a4845f39392c8ec3b6834f03d4594d7e4f40292051facf83fc6dc44b1",
                 "6ce49ba2b2548ec35968b740706f8994f7237870cd0a0ab29ad00bc6f631032b",
                 "5c4020dc2d7b6c0be3918883fac992d606f52303d26cebb140411bbad46311bb",
                 "3bcafa7d4afd7b3ff8d7d309dbdec88441ca5e0e0466cc6477cee52125729553",
                 "02e6cdfe9ba397c2dc534734a0b937f89777eb5a3f5b8f0162644a55a0a4585c",
                 "4ea137e2c7d57d0d166a04deb55fe0e30c94b1ce0248d0f8c800d6a284d070a8",
             ]},
        ]},
    3: {'location': "II.4–5, XIII.499,5–500,15 K.",
        'greek': "78077bb2eecb1de42f0dc93004d81578c7f19fa7650034cf4d8a554372bbc647",
        'refs': [
            {'translator': "Marai", 'words': 335, 'begins': "But I will", 'ends': "with a cerate.",
             'raw': "8243400418f5b4fe076bd2474bec3b9ca5966ec69dd27e8f43f56f48251c2fb7",
             'normalized': "707183a03b658a9e25ff120849e094d18c6f6b8fba18203688bbd09806009206",
             'sentences_normalized': [
                 "60bb986c981f1517b07b4baf299fbd08a1f6d33f73dcabb25d761a78640a9229",
                 "540dd397b2d380dcc3f59796c4facc43379929f1a3b5e6cc9a218274391b635b",
                 "5d2b47c086cd227546b14e7e8fcf49b8cab0bbd7d5cd0973a30442064e893d3c",
                 "ffe09e5fbb16af0f1ac6eb7d30f8aa8193c6224709a8b5e47b9a7b5693b7323e",
                 "98b58d910e86bc74d08a4438036d27e7160ad928aa5087012bade5e3340ba687",
                 "1b0797f5919dd72b8dd3c91f0c3ceeaa4042a44abaf2b4a7f5db696283a24c2a",
                 "e3cdf6786266ddfbc16f5a7e92798bf47ded194c6b1eadbce07b46bede4ff38b",
                 "2a9ce51fe2a804c29f09e71010a3e318aa483ca7f6eb25cdd7eeeb46e66484bd",
                 "32a1e4fd387b35ef4ac42bd6fd9af450461a4d2eb5d9fd6b6b66735e27c7d4a1",
                 "9bd8c3fd36097c0d3a522ca900ec57baeb90670a6746a37206518d905cbbf406",
                 "69eba276557e4b1a34bc270d5c70164b3a6a8e5d3fd859461e24e82a74f36066",
                 "8a8d6a33e7070c3186bf0ef08679b5eaef31120395218ab644c93489a34d1152",
             ],
             'sentences_raw': [
                 "60bb986c981f1517b07b4baf299fbd08a1f6d33f73dcabb25d761a78640a9229",
                 "540dd397b2d380dcc3f59796c4facc43379929f1a3b5e6cc9a218274391b635b",
                 "5d2b47c086cd227546b14e7e8fcf49b8cab0bbd7d5cd0973a30442064e893d3c",
                 "ffe09e5fbb16af0f1ac6eb7d30f8aa8193c6224709a8b5e47b9a7b5693b7323e",
                 "98b58d910e86bc74d08a4438036d27e7160ad928aa5087012bade5e3340ba687",
                 "538eeadf13295fa08b7d2bd51ba22283fa65c76b2627c3e866128dbd8213546d",
                 "e3cdf6786266ddfbc16f5a7e92798bf47ded194c6b1eadbce07b46bede4ff38b",
                 "2a9ce51fe2a804c29f09e71010a3e318aa483ca7f6eb25cdd7eeeb46e66484bd",
                 "291480265669838d75c333bcfcef3d8f63e81e085adcf2b8c9e9a603668795f5",
                 "9c7e5354c9527d6eba3974f42b7f556a4f0e5620f567966c81eb4823dcb507f0",
                 "69eba276557e4b1a34bc270d5c70164b3a6a8e5d3fd859461e24e82a74f36066",
                 "8a8d6a33e7070c3186bf0ef08679b5eaef31120395218ab644c93489a34d1152",
             ]},
        ]},
    4: {'location': "III.2, XIII.569,10–570,17 K.",
        'greek': "860e3a87d3f230c418c6cc948960a7271da6b3d5c0f32dfa86af3b86ca980683",
        'refs': [
            {'translator': "Marai", 'words': 310, 'begins': "Among the substances", 'ends': "windows facing south.",
             'raw': "25e093764617b5bb3a3257e732245527ac6f769c0572b250907d53366e74ff11",
             'normalized': "c0ddd86ed25198d19a58d45b76e270b04eab49dc376e2948e39c20312078dd36",
             'sentences_normalized': [
                 "76fcabe675a107d7c678c9be63268f4cf712b7c1c0bcd232d521dc2ba4faa252",
                 "e80a44ecf09f4485c902f3b2bafd3ec8600f47abfb97c55672e2e40de88ab86b",
                 "39196b60c56bfd427753ae5c9aeccc2217e472a144ddfb23e33d2a04f722235d",
                 "645604746ae376cfab72d4ab66e7c946d4a8ba0b467d56a544890c864da5c4cd",
                 "e166666b7e05232fc4d1b4b2bd73aae8ecf8ca0eb536acb1cd51d656f7c414ed",
                 "a8dede08baf76bfc360012b3c29f33625458bc669f136c30bbabcb2c1dd8183d",
                 "cdbc72d565169a235ff194b6a885a19c0817be46750d8a0a15c6dba915bf0fcd",
                 "f0ba3a3e289633ba3f8b073ff2d93b63bc448993e211cc7bdc7e743a6169fe7b",
             ],
             'sentences_raw': [
                 "76fcabe675a107d7c678c9be63268f4cf712b7c1c0bcd232d521dc2ba4faa252",
                 "d4f3769eff113cb7445005df62e091dc74d29b470693b26881f48dde574e3a64",
                 "39196b60c56bfd427753ae5c9aeccc2217e472a144ddfb23e33d2a04f722235d",
                 "c87c3ee5e2a313c89d5e828ed9dac3cf308845c1d79eb41d76e5650ce19c1f92",
                 "e166666b7e05232fc4d1b4b2bd73aae8ecf8ca0eb536acb1cd51d656f7c414ed",
                 "a8dede08baf76bfc360012b3c29f33625458bc669f136c30bbabcb2c1dd8183d",
                 "cdbc72d565169a235ff194b6a885a19c0817be46750d8a0a15c6dba915bf0fcd",
                 "f0ba3a3e289633ba3f8b073ff2d93b63bc448993e211cc7bdc7e743a6169fe7b",
             ]},
        ]},
    5: {'location': "III.7–8, XIII.635,6–636,14 K.",
        'greek': "61aa8d23a8f9fdba5b6f749148dce7dc1fc123736e59797a3ed32a0cec86117d",
        'refs': [
            {'translator': "Marai", 'words': 314, 'begins': "A thick composition", 'ends': "could cure all.",
             'raw': "c6a27020e165a909aa9f49caac6f604a29fa90d2e9fb17fcc60da8a3498e45b4",
             'normalized': "910a8f16090459e575385eb5bbaafc51f9b503a46aee7fa3e98507a8089b9089",
             'sentences_normalized': [
                 "0a987e9831b3d719961bf689c10eef8c4f3da291ded0d64272fc5bf8e62e8fad",
                 "63414d40feffdac70629eaedf73be9629972f80c814719ff81e4e1876e7a1960",
                 "26a15594e9f4e17ea71165526f857b202d4e9697dfe18d1a155b69a21fa7f523",
                 "040330e211ccf6d5a41f9fd3d3d16101ef47c2b5a9ea118e531a032225ea6c51",
                 "6ce012fd1056714b493ab0a7b473923e52b597bdb7cde60a0d97ef6f54e60c4d",
                 "1697d7bfa0631fedd48a7c1c71e0f6b0601965585660280e327c84959f328573",
                 "0792d09901afb85dc7073f957e17deb3dbb7df113c49cfa8d15ad610f98addf7",
                 "3fdc6bead10866ef791f9411073e8bd9effb956de164311d0280674fde83812e",
                 "dd769a078db3ce21e5addf9ecf1d86ce8fee684734edcabf54ff8235a8843370",
                 "331e96fca4ea405943ade68d2bde0e04912c4078a24046ae322c91a5887f9706",
                 "f8c02f7639ea40dea5eb556e8fbb493ddef836be3aaa96a13b508b999f313bba",
             ],
             'sentences_raw': [
                 "0a987e9831b3d719961bf689c10eef8c4f3da291ded0d64272fc5bf8e62e8fad",
                 "1ce8c7d0672844b596a2096f43790297146557e819e095f274fce58b81911e4a",
                 "e3c23f6b70e0ae995acb2099d2ad8d159a5428eb79c79d5fc50adfb55e50891a",
                 "040330e211ccf6d5a41f9fd3d3d16101ef47c2b5a9ea118e531a032225ea6c51",
                 "6ce012fd1056714b493ab0a7b473923e52b597bdb7cde60a0d97ef6f54e60c4d",
                 "1697d7bfa0631fedd48a7c1c71e0f6b0601965585660280e327c84959f328573",
                 "0792d09901afb85dc7073f957e17deb3dbb7df113c49cfa8d15ad610f98addf7",
                 "3fdc6bead10866ef791f9411073e8bd9effb956de164311d0280674fde83812e",
                 "dd769a078db3ce21e5addf9ecf1d86ce8fee684734edcabf54ff8235a8843370",
                 "331e96fca4ea405943ade68d2bde0e04912c4078a24046ae322c91a5887f9706",
                 "f8c02f7639ea40dea5eb556e8fbb493ddef836be3aaa96a13b508b999f313bba",
             ]},
        ]},
    6: {'location': "IV.5, XIII.703,8–704,13 K.",
        'greek': "98986a922891af49ce6585a6695ae7bebb4c849d8b87a7986f574d0e03856a26",
        'refs': [
            {'translator': "Marai", 'words': 240, 'begins': "The thickness of", 'ends': "hard-to-heal chronic wounds.",
             'raw': "ca318413bf8bb53eb34ed535f6d660568dc9b99ea55bc7ee390d4616da280dc3",
             'normalized': "e8d111f66f5c0c854e578637316a22965796a5a151f910fba5699760f45caf35",
             'sentences_normalized': [
                 "dfae79e41cec160a9dc55b4ae014bf2687229f3b59f3e2f28cc3c20735e91b92",
                 "f5ab17a5dc4bc032e9d89e4b89108997e66e7b4d92df276874e14b484006afc5",
                 "e29ddb884133bfef40bb85c5b36abaaf74278331c810e48706cc954bbe473080",
                 "559f56d884f31b95614fdd3bacdf38624501e3bc533c3df721c6597a26ea88e0",
                 "a95eb5b23ee8189c984d3474c07c9a95af31f387e9d7f5cea261cc659e9032b0",
                 "ae133e0fd7e1c1472e5657faa3cb4f3962caa0413b9d0fb3b3106c07b6ffc644",
                 "4f7ca42fc13aac60cb9a06ac0cc3509f11bcf48e63aade0ecc417120a3c72c06",
                 "dfe6ece2df158c87535c74c5a73c4c98f6d1ce1b67ef8b1a4ae4d764af07d4c2",
             ],
             'sentences_raw': [
                 "dfae79e41cec160a9dc55b4ae014bf2687229f3b59f3e2f28cc3c20735e91b92",
                 "f5ab17a5dc4bc032e9d89e4b89108997e66e7b4d92df276874e14b484006afc5",
                 "5a01472da9d006bb52d915474c7defa172b9b7dba83704f5344a2c258b0ae229",
                 "559f56d884f31b95614fdd3bacdf38624501e3bc533c3df721c6597a26ea88e0",
                 "a95eb5b23ee8189c984d3474c07c9a95af31f387e9d7f5cea261cc659e9032b0",
                 "577c5c790028040c9a2125334894a658926ce1696070f072435d198027dfb6fa",
                 "4f7ca42fc13aac60cb9a06ac0cc3509f11bcf48e63aade0ecc417120a3c72c06",
                 "dfe6ece2df158c87535c74c5a73c4c98f6d1ce1b67ef8b1a4ae4d764af07d4c2",
             ]},
        ]},
    7: {'location': "V.2, XIII.771,18–773,9 K.",
        'greek': "bf154e3bcfeff2bc8b7f4426c4ac0569f487bfef5d19e1c80a85c4440787e6b4",
        'refs': [
            {'translator': "Marai", 'words': 280, 'begins': "Ampelitis [i.e unidentified", 'ends': "to the remedy.",
             'raw': "465bf3f34dd51bc52d95461cf885fcf53db4a640c72848ee405e9504e0e8f152",
             'normalized': "c4d33dc7f6ea39e95922373ddc57e4061a60fd37f83b69fe5b4a1fec80568573",
             'sentences_normalized': [
                 "f17ed28517a9b7edde645e4300bafd13e0354271f219224ce8b0688b54a00a53",
                 "d9d787237df29321145fd0907ece7a2f20c575a9708cf09a46906cebb1acf852",
                 "c5d8f6c8a9542642e1dc282b3814035753f51bd02c5e3fbc9d245d26098b3a5c",
                 "7828cf4c8808a30e7a55032677bf39339919c092c4adcf43a2ac7afb12451952",
                 "0cc94fb98e3a49d96970175ac7f6ab1d608396ed7b073398fd85e5f07cf0aa1e",
                 "ee67d9ddabfdd77ab40d549bdd66bd30c3a3b55b875bc682ece0521ffbbbf8c5",
                 "e456f166a6b0193c351486ef468d1e11220420a869aee4a2e3d2e878e4e69486",
                 "87b217da2d8fd37827a57e1ba5a08309242404944e6d264261a6cdc8ee92a36e",
                 "fe8d4cac25ed2f34a7b48463e6ed77db9169c0c0fa981c5975ddd6e43cfa749f",
                 "0563e0010b5c250d9cee71a4cb7029a9ead4a783e8265f285c1a5bcc8f887b91",
                 "3570853735da2f0f017a86f96d2a878193fa0f17ab210f9ce24d2a02de73cd82",
             ],
             'sentences_raw': [
                 "f17ed28517a9b7edde645e4300bafd13e0354271f219224ce8b0688b54a00a53",
                 "d9d787237df29321145fd0907ece7a2f20c575a9708cf09a46906cebb1acf852",
                 "c5d8f6c8a9542642e1dc282b3814035753f51bd02c5e3fbc9d245d26098b3a5c",
                 "7828cf4c8808a30e7a55032677bf39339919c092c4adcf43a2ac7afb12451952",
                 "0cc94fb98e3a49d96970175ac7f6ab1d608396ed7b073398fd85e5f07cf0aa1e",
                 "fef0ca6b28dbf4100b5339f0d0a9b574d012b5686dec7a10806c4ca52cd28602",
                 "e456f166a6b0193c351486ef468d1e11220420a869aee4a2e3d2e878e4e69486",
                 "87b217da2d8fd37827a57e1ba5a08309242404944e6d264261a6cdc8ee92a36e",
                 "9eeae172635336232ec86590b8cfb28458f5a888a05eb59bd0813353674a1698",
                 "0563e0010b5c250d9cee71a4cb7029a9ead4a783e8265f285c1a5bcc8f887b91",
                 "e0b1cbf68cbaf03c159b2f1b805fbdb1cfc36429894b11ef47e93738df031a3e",
             ]},
        ]},
    8: {'location': "V.13, XIII.840,10–842,1 K.",
        'greek': "1f5b0576b2a6085c355c41c56583af5546b2686b214ba0bd7f79701e6bb9be61",
        'refs': [
            {'translator': "Marai", 'words': 308, 'begins': "Sitz bath for", 'ends': "with rose oil.",
             'raw': "aa6c1a0cc6f7aa32a0e6bbf99db4d76ac370524596becda6d398f907ebf2fa9b",
             'normalized': "acd49bda3380e73da9824ccdf31a3c248f8b912999e35459ac692666b64b67a9",
             'sentences_normalized': [
                 "dfded9be09f52f065c35f41509d82e6cafc862c1ee8a893dca873b3ce2e3aa4f",
                 "bbf9150dfeda944951f15c582e7c06d817a5e3cb40f0db89455e871fd54e54ba",
                 "9438da21aef265a7518d0386075c697a0941a509144ab7e3073d9fca0a4c8cac",
                 "30f1fb4db81d94e6612b5ea8a31b88b8376d59896c03843c69c88eb74c0f7fa2",
                 "22ba84b54dff4abad98b404ca6d3b7a0ffa4dc79f7f2eae7aaaaf998b7ef6382",
                 "9704d9649a3e7c9ab056aa387bcf035e6a7d1a628e2001cac436e8f60c5084d1",
                 "001ade69b593d424ddf6b40ce539146c14e8f35232c36ba52966f02e882d8475",
                 "55c25d9b1dec6850fa6e746762cd7a989dfbb79f6a10e9f730c6831ac5315c4f",
                 "4b08690834344db8388a87a6adcc49a252b66a332de7637ec8a650eb144e74a0",
                 "71a8ccd2f71778f22daf0bc013bcfb39d16246f74f2889a4318852f1ea5b61c7",
                 "9997cf50c9015980cac3655056f7daeb5d656f849a3fbe432f69a54f27ac30d1",
                 "2e9e134a18a560de3b0320bf2e990023f1797c74e8b2866e785fe3f688948194",
                 "f2a60248ed71aa8c5c13f8e75c91ab1b8c1e0ddf4097a5f3ec0896d4d6a7e061",
                 "b41d7c889a4dbaf3943dd29a0c6eaa07deb608c0899df8d35aa6039c82478e6a",
                 "e915d415f43daf6d01e1bb52bfc910b39dd5d8255cb97640a6195d25c29acb2c",
                 "557a86288783b6e3282196b4f8eab380640472e15cecf948498c9435ab9b6b35",
                 "8750fcc630bec78d75ceff0d26752c0572374ab44e5ba769999b9eb4741b0c19",
                 "ebbf9b43caabecbcb83e40acd970e0c64b99b29cb9006b2da5082885dd57e5dc",
                 "19de1f188b105566884b949eaefc3a5a14dad49b52db3190fc408e647e1db82f",
                 "d5534d826e76ef2fd7687aa19debd7a441a31f0391ac07d128e31704c54e6afd",
                 "0328b3f76110c54e594f7a40cf1f28c250f0b45adb9a46a1343f059046e8956b",
                 "dcba5dac47b9e478692384e88b5d8f671408f0bb8c0c272cbb5e43368af30b6f",
                 "54526a0f1d9bc0631045b24cd4e6d4d3fbb7ae8866ef768856a72126744b857f",
                 "954e8adbef95f6a0d1b2d1d0692d9ad302b803dfa25237ea7f99554815cb8797",
                 "45d460aeb7af92bb55b79cbed3eac2edafbf560c700c9bef3df46b7dae62eb87",
                 "226f43630ec1169d121f26c3fd3a291ab0e48137c314b2c2146b9135cd2b3057",
                 "93d830dfccceab143f9f6da03922e597959ef747e8a28d3c0f6de2522b605174",
                 "0b8f373614824d5e9d0a24af4730f22776e87fd6bc04f037de59b5059cfbfdbd",
                 "a1f3e1fefa5aee6c9d787f3fdba16bf782171de6d2792cb154358b45b49921f6",
                 "93d830dfccceab143f9f6da03922e597959ef747e8a28d3c0f6de2522b605174",
             ],
             'sentences_raw': [
                 "dfded9be09f52f065c35f41509d82e6cafc862c1ee8a893dca873b3ce2e3aa4f",
                 "bbf9150dfeda944951f15c582e7c06d817a5e3cb40f0db89455e871fd54e54ba",
                 "9438da21aef265a7518d0386075c697a0941a509144ab7e3073d9fca0a4c8cac",
                 "30f1fb4db81d94e6612b5ea8a31b88b8376d59896c03843c69c88eb74c0f7fa2",
                 "22ba84b54dff4abad98b404ca6d3b7a0ffa4dc79f7f2eae7aaaaf998b7ef6382",
                 "9704d9649a3e7c9ab056aa387bcf035e6a7d1a628e2001cac436e8f60c5084d1",
                 "001ade69b593d424ddf6b40ce539146c14e8f35232c36ba52966f02e882d8475",
                 "55c25d9b1dec6850fa6e746762cd7a989dfbb79f6a10e9f730c6831ac5315c4f",
                 "4b08690834344db8388a87a6adcc49a252b66a332de7637ec8a650eb144e74a0",
                 "71a8ccd2f71778f22daf0bc013bcfb39d16246f74f2889a4318852f1ea5b61c7",
                 "9997cf50c9015980cac3655056f7daeb5d656f849a3fbe432f69a54f27ac30d1",
                 "2e9e134a18a560de3b0320bf2e990023f1797c74e8b2866e785fe3f688948194",
                 "f2a60248ed71aa8c5c13f8e75c91ab1b8c1e0ddf4097a5f3ec0896d4d6a7e061",
                 "b41d7c889a4dbaf3943dd29a0c6eaa07deb608c0899df8d35aa6039c82478e6a",
                 "e915d415f43daf6d01e1bb52bfc910b39dd5d8255cb97640a6195d25c29acb2c",
                 "557a86288783b6e3282196b4f8eab380640472e15cecf948498c9435ab9b6b35",
                 "8750fcc630bec78d75ceff0d26752c0572374ab44e5ba769999b9eb4741b0c19",
                 "ebbf9b43caabecbcb83e40acd970e0c64b99b29cb9006b2da5082885dd57e5dc",
                 "19de1f188b105566884b949eaefc3a5a14dad49b52db3190fc408e647e1db82f",
                 "d5534d826e76ef2fd7687aa19debd7a441a31f0391ac07d128e31704c54e6afd",
                 "0328b3f76110c54e594f7a40cf1f28c250f0b45adb9a46a1343f059046e8956b",
                 "dcba5dac47b9e478692384e88b5d8f671408f0bb8c0c272cbb5e43368af30b6f",
                 "54526a0f1d9bc0631045b24cd4e6d4d3fbb7ae8866ef768856a72126744b857f",
                 "954e8adbef95f6a0d1b2d1d0692d9ad302b803dfa25237ea7f99554815cb8797",
                 "45d460aeb7af92bb55b79cbed3eac2edafbf560c700c9bef3df46b7dae62eb87",
                 "226f43630ec1169d121f26c3fd3a291ab0e48137c314b2c2146b9135cd2b3057",
                 "93d830dfccceab143f9f6da03922e597959ef747e8a28d3c0f6de2522b605174",
                 "0b8f373614824d5e9d0a24af4730f22776e87fd6bc04f037de59b5059cfbfdbd",
                 "a1f3e1fefa5aee6c9d787f3fdba16bf782171de6d2792cb154358b45b49921f6",
                 "93d830dfccceab143f9f6da03922e597959ef747e8a28d3c0f6de2522b605174",
             ]},
        ]},
    9: {'location': "VI.10, XIII.909,17–911,7 K.",
        'greek': "8c6bb47e9a347a29b6ad74cb041cfb6deecbe6dc9ee626ee9b39ffbe4451cf07",
        'refs': [
            {'translator': "Marai", 'words': 245, 'begins': "Terebinth resin, 48", 'ends': "to 8 drachmai.",
             'raw': "d711b33d3dbfea92139f990ef9242123cdcd9bb990e7afe1ae8273529ddc5eb6",
             'normalized': "eb576e8d86275495af3d36b73b218233c889ecc53b1102b520d20b4590fcc3ee",
             'sentences_normalized': [
                 "b0900077fca3bd2e69ca0616a1c2de13f1e591213d1a63c5e6ae2d6be7954932",
                 "c2155d0d7d3f2c32a4c7b686941e242b1739b029b988e1c4c2e622abe409489b",
                 "a9f92e111a8bda78df13ce1cee03bc2d46dd4c6ab8c50795fce4449e94a8e57d",
                 "a6ff54de22a380e3653ccb10227b77c81b9d27f9d4fbb001b21dc3cb1c8f0c3d",
                 "a7111982e76f5194be66a810434958737dffd7468e9fccdeb6c84f0d881b68a2",
                 "b65ae08293d60218129b5a3013a81ecdd72c00c149dc0cd27fad6bc606a38aa5",
                 "fe4a2ca85fc8c2a5566377cedef3e0c75bf20808ca59b72f1c7c12d25be74aee",
                 "124f1e46240217aed441f6ade0e83a546be290745b5cf6088a21cc1bdb31c906",
                 "39e7d6b505910ed732eb02db7205e1a6b8355e09916a09dc22d47ef5af7ecec0",
                 "c343a6282aa15fc27895d38c50ea381e4e9b70ee9c3ac215b4db780c3b3ca50c",
                 "a8d35696272c80c6ae866638abbea32bb6885831647237a7e5323b07a3f127b2",
             ],
             'sentences_raw': [
                 "b0900077fca3bd2e69ca0616a1c2de13f1e591213d1a63c5e6ae2d6be7954932",
                 "c2155d0d7d3f2c32a4c7b686941e242b1739b029b988e1c4c2e622abe409489b",
                 "a896485ac1bd2e3f4fd858efba0faffc9187dd31834a5880c91b20814d9c5a26",
                 "a6ff54de22a380e3653ccb10227b77c81b9d27f9d4fbb001b21dc3cb1c8f0c3d",
                 "a7111982e76f5194be66a810434958737dffd7468e9fccdeb6c84f0d881b68a2",
                 "b65ae08293d60218129b5a3013a81ecdd72c00c149dc0cd27fad6bc606a38aa5",
                 "fe4a2ca85fc8c2a5566377cedef3e0c75bf20808ca59b72f1c7c12d25be74aee",
                 "124f1e46240217aed441f6ade0e83a546be290745b5cf6088a21cc1bdb31c906",
                 "8d4b90f7d0a73e8556260ff76a241b985db14b2872507d55b57c229529e6d3e4",
                 "c343a6282aa15fc27895d38c50ea381e4e9b70ee9c3ac215b4db780c3b3ca50c",
                 "a8d35696272c80c6ae866638abbea32bb6885831647237a7e5323b07a3f127b2",
             ]},
        ]},
    10: {'location': "VII.7, XIII.983,3–984,8 K.",
        'greek': "be3ccaa563b4b306a5e9c63a616f80f031b9a82a691f0892d513bc5ad32a4354",
        'refs': [
            {'translator': "Marai", 'words': 275, 'begins': "[ingredient] 10 [drachmai];", 'ends': "drachmai each; frankincense.",
             'raw': "7f240de02effcd9d2bea0488635f116eed8d021fd1a7186cc28f5ca54f9107e5",
             'normalized': "91d92ca4ffe5ec33f030967b9a30e8a5eb4fd6432b15178725c12a113b31e645",
             'sentences_normalized': [
                 "a03a9d82a3fdec60c959f02cd5c3b97e93c7a02e46367f321eb30fb13769544d",
                 "382584f2456ef4ea242137b1acb0d1eb6bb0b1ba597a117d464e437651839f9b",
                 "bd67970f1f5682268388d3ccb602fa1466060a2f8716d818782eacda28681110",
                 "6efeec6a53285c305ca458db7b3de59f31b4ee95892ee7352a7eab74ebfc1b52",
                 "e6facc6f09a28d3836e2433a829ffa625973461db9cb4bbb3aa563f24a8ecd8e",
                 "53216029a2e9802180f0d94fe3bec3f2c0e29d252c45283177247d5884be0bb4",
                 "b0d1f1b84228224f7b0b7ea9624be0ca5d52e5b13b664570c475d2d54bcd1296",
                 "6e2ff6acefa9d0cc3a7753f60a80d5075f6fe15176521eb93dd16d7b173de11c",
                 "1df1c03cea8365c31b1e827b9841aae07e62951e459e9ee6f2aaa722bfea68c8",
                 "9fc557c634c29335cea28aae94b8fedce90c88e8d08a94b08355d9c939daceee",
                 "9f9d0b1969703e6383bc903320bf290be21c526340520e9e1ea9176576e7d861",
                 "c198dfd4775cfb70988e03d606a702f119dff110773e283c5e7a76030eb1b5cf",
             ],
             'sentences_raw': [
                 "a03a9d82a3fdec60c959f02cd5c3b97e93c7a02e46367f321eb30fb13769544d",
                 "382584f2456ef4ea242137b1acb0d1eb6bb0b1ba597a117d464e437651839f9b",
                 "bd67970f1f5682268388d3ccb602fa1466060a2f8716d818782eacda28681110",
                 "6efeec6a53285c305ca458db7b3de59f31b4ee95892ee7352a7eab74ebfc1b52",
                 "e6facc6f09a28d3836e2433a829ffa625973461db9cb4bbb3aa563f24a8ecd8e",
                 "53216029a2e9802180f0d94fe3bec3f2c0e29d252c45283177247d5884be0bb4",
                 "b0d1f1b84228224f7b0b7ea9624be0ca5d52e5b13b664570c475d2d54bcd1296",
                 "6e2ff6acefa9d0cc3a7753f60a80d5075f6fe15176521eb93dd16d7b173de11c",
                 "1df1c03cea8365c31b1e827b9841aae07e62951e459e9ee6f2aaa722bfea68c8",
                 "9fc557c634c29335cea28aae94b8fedce90c88e8d08a94b08355d9c939daceee",
                 "9f9d0b1969703e6383bc903320bf290be21c526340520e9e1ea9176576e7d861",
                 "c198dfd4775cfb70988e03d606a702f119dff110773e283c5e7a76030eb1b5cf",
             ]},
        ]},
}
FILES = {   # the file each check expects: SHA-256 and layout (H = Chunk line, B = blank, T = text)
    'post-fix': {'sha256': "5e6c7c7a02ae3d8761ea0236bc45b4f1789dafe13a9c066e299b0ed27c642076",
                 'description': 'mt_eval/input/on_mixtures.txt as evaluated (after the reference fix)',
                 'skeleton': "HBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBB"},
    'pre-fix': {'sha256': "07af3ce679e91a3f5244dd02d4dfb796b0f9fba5fae7a4ad8019d9e0881bd98a",
                'description': 'analysis/data/mixtures_pre_fix/on_mixtures.txt as evaluated (before the fix)',
                'skeleton': "HBTBTBTBHBTBTTBHBTBTBTBHBTBTTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBHBTBTBTBB"},
    'comp': {'sha256': "92850bd0d99c05e11afc391c502e6d53885717817aea547b692e1204370a459a",
             'description': 'mt_eval/input/on_comp.txt',
             'skeleton': "HTBTBHTBTBHTBTBHTBTBHTBTBHTBTBHTBTBHTBTBHTBTBHTBTBBB"},
}
DISTRIBUTED = {   # the two files as distributed, without the English
    "4c8ed1e9af31b1f88967a6ec7bbced9e7442c07215fc825888711abeb6dc3206": 'this is mt_eval/input/on_mixtures.txt as distributed, without the English',
    "2456e74412d172a75fe0711f02615367d82601bb06cb6076c4b72f828808a950": 'this is the pre-fix copy as distributed, without the English',
}


def kind(line):
    if re.fullmatch(rb'Chunk \d+', line):
        return 'H'
    return 'B' if not line.strip() else 'T'


def segments(skeleton):
    """The skeleton cut at each Chunk line: [(passage index from 1, its letters)], plus any text before
    the first Chunk line as passage 0."""
    head, rest = re.match(r'([^H]*)(.*)', skeleton).groups()
    return ([(0, head)] if head else []) + list(enumerate(re.findall(r'H[^H]*', rest), 1))


def words3(text, end=False):
    w = text.split()
    return ' '.join(w[-3:] if end else w[:3])


def where(expected, found_hashes, found_text):
    """Which sentences differ: compare the hashes from the start and from the end."""
    n, m = len(expected), len(found_hashes)
    if found_hashes == expected:
        return 'every sentence matches; the difference is in the spaces between sentences or at the ends of the line'
    head = 0
    while head < n and head < m and expected[head] == found_hashes[head]:
        head += 1
    tail = 0
    while tail < n - head and tail < m - head and expected[n - 1 - tail] == found_hashes[m - 1 - tail]:
        tail += 1
    e_first, e_last, f_count = head + 1, n - tail, m - tail - head
    yours = f"; your sentence {head + 1} begins '{words3(found_text[head])}'" if f_count > 0 else ''
    if e_first > e_last:
        return f'text added after sentence {head} of {n}{yours}'
    if f_count == 0:
        span = f'sentence {e_first}' if e_first == e_last else f'sentences {e_first}-{e_last}'
        return f'{span} of {n} missing'
    span = f'sentence {e_first}' if e_first == e_last else f'sentences {e_first}-{e_last}'
    more = '' if m == n else f' (your text has {m} sentences)'
    return f'{span} of {n} differ{"s" if e_first == e_last else ""}{more}{yours}'


def check_reference(line, ref):
    """(passed, verdict) for one reference line."""
    if line is None:
        return False, 'FAIL  missing'
    if line.strip() == POINTER:
        return False, 'FAIL  not rebuilt (the pointer line is still in place)'
    if sha256(line) == ref['raw']:
        return True, f"PASS  byte-identical ({ref['words']} words)"
    text = line.decode('utf-8', 'replace')
    if sha256(normalize(text).encode('utf-8')) == ref['normalized']:
        found = sentences_raw(text)
        return False, ('FAIL  same text after normalization, but the typography differs (quotes, dashes, spaces, '
                       'invisible or compatibility characters): '
                       + where(ref['sentences_raw'], [sha256(s.encode('utf-8')) for s in found], found))
    found = sentences_normalized(text)
    notes = [where(ref['sentences_normalized'], [sha256(s.encode('utf-8')) for s in found], found)]
    if len(text.split()) != ref['words']:
        notes.append(f"{len(text.split())} words, expected {ref['words']}")
    if words3(text) != ref['begins']:
        notes.append(f"begins '{words3(text)}', expected '{ref['begins']}'")
    if words3(text, end=True) != ref['ends']:
        notes.append(f"ends '{words3(text, end=True)}', expected '{ref['ends']}'")
    return False, 'FAIL  the text differs: ' + '; '.join(notes)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('file', type=Path)
    ap.add_argument('--pre-fix', action='store_true',
                    help='check against the pre-fix file (analysis/data/mixtures_pre_fix/on_mixtures.txt)')
    args = ap.parse_args()
    data = args.file.read_bytes()
    lines = [x[:-1] if x.endswith(b'\r') else x for x in data.split(b'\n')]
    chunks, current = {}, None
    for line in lines:
        if kind(line) == 'H':
            current = int(line.split()[1])
            chunks[current] = []
        elif current is not None and line.strip():
            chunks[current].append(line)
    first_greek = (chunks.get(1) or [b''])[0]
    if sha256(first_greek) == COMP[1]['greek']:
        work, table, layout = 'Comp.', COMP, 'comp'
    else:
        work, table = 'Mix.', MIX
        layout = 'pre-fix' if args.pre_fix or args.file.resolve().parent.name == 'mixtures_pre_fix' else 'post-fix'
    target = FILES[layout]
    problems, identical, n_refs = 0, 0, 0
    whole = sha256(data)
    print(f'{args.file}: {len(data):,} bytes, sha256 {whole}')
    print(f"checked against: {target['description']}")
    if whole == target['sha256']:
        print('whole file   PASS  byte-identical')
    else:
        problems += 1
        hints = [DISTRIBUTED[whole]] if whole in DISTRIBUTED else []
        if b'\r\n' in data:
            hints.append('it has CRLF line endings; the original has LF')
        if data.startswith(b'\xef\xbb\xbf'):
            hints.append('it starts with a byte-order mark; the original does not')
        print('whole file   FAIL  not byte-identical' + (f" ({'; '.join(hints)})" if hints else ''))
    skeleton = ''.join(kind(x) for x in lines)
    if skeleton == target['skeleton']:
        print('layout       PASS')
    else:
        problems += 1
        print('layout       FAIL  the lines are not laid out as in the original:')
        if layout == 'post-fix' and skeleton == FILES['pre-fix']['skeleton']:
            print('    (this is the layout of the pre-fix copy; if that is the file you are rebuilding, use --pre-fix)')
        expected, found = dict(segments(target['skeleton'])), dict(segments(skeleton))
        for i in sorted(set(expected) | set(found)):
            e, f = expected.get(i), found.get(i)
            if e == f:
                continue
            label = f'{work} {i}' if i else 'before the first Chunk line'
            print(f"    {label}: expected {', '.join(LINE_KIND[c] for c in e) if e else 'nothing'}; "
                  f"found {', '.join(LINE_KIND[c] for c in f) if f else 'nothing'}")
            if f and 'TT' in f and not (e and 'TT' in e):
                print('        two text lines with no blank line between them: each reference needs its own '
                      'line with a blank line before and after it (the pre-fix defect)')
    for n in range(1, 11):
        location, greek, refs = table[n]['location'], table[n]['greek'], table[n]['refs']
        found = chunks.get(n) or []
        n_refs += len(refs)
        print(f'\n{work} {n}  ({location})')
        if not found:
            print('    FAIL  passage missing')
            problems += 1 + len(refs)
            continue
        ok = sha256(found[0]) == greek
        problems += not ok
        print(f"    {'Greek':<22}  {'PASS' if ok else 'FAIL  differs from the Greek of the evaluation'}")
        for slot, ref in enumerate(refs, 1):
            passed, verdict = check_reference(found[slot] if slot < len(found) else None, ref)
            identical += passed
            problems += not passed
            print(f"    {ref['translator']:<22}  {verdict}")
        if len(found) > len(refs) + 1:
            print(f'    FAIL  {len(found) - 1} reference lines, expected {len(refs)} (each translation must be one line)')
            problems += 1
    print(f'\n{work}: {identical} of {n_refs} references byte-identical; {problems} problem(s).')
    print('PASS' if problems == 0 else 'FAIL')
    return 0 if problems == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
