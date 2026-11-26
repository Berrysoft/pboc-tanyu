# pboc-tanyu

解析 **PBOC**（“基于文献的上古汉语”）的 IPA 拟音，并由音节推导中古声母。

包只导出四个函数：

```python
from pboc_tanyu import mc_grade, mc_initials, mc_rhyme, parse_syllable
```

- `parse_syllable(ipa)`：把一条拟音拆成
  **声母 + 是否咽化 + 是否带 -r- + 主元音 + 韵尾 + 声调**。
- `mc_initials(syllable)`：只接受 `parse_syllable` 返回的 `Syllable`，
  返回**一个**中古声母（传统字母，如 `幫`、`知`、`羣`）。
- `mc_grade(syllable)`：只接受 `Syllable`，返回切韵等第 **1–4**。
- `mc_rhyme(syllable)`：只接受 `Syllable`，返回 **`(開/合, 韵)`**。

## 安装

```bash
pip install -e .
```

要求 Python ≥ 3.9，运行时无第三方依赖。

## `parse_syllable`

```python
>>> from pboc_tanyu import parse_syllable
>>> parse_syllable("pˤrak")
{'initial': 'p', 'pharyngealized': True, 'has_r': True, 'vowel': 'a',
 'coda': 'k', 'tone': '入', 'tone_marker': ''}

>>> parse_syllable("sra")
{'initial': 's', 'pharyngealized': False, 'has_r': True, 'vowel': 'a',
 'coda': '', 'tone': '平', 'tone_marker': ''}
```

返回普通 `dict`（静态类型上对应 `pboc_tanyu.Syllable`）：

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `initial` | `str` | 声母，如 `p`、`pʰ`、`n̥`、`st`、`C.r` |
| `pharyngealized` | `bool` | 是否咽化（非三等），即是否带 `ˤ`（或 `◌̙`） |
| `has_r` | `bool` | 声母后是否带 -r- 介音 |
| `vowel` | `str` | 主元音：`a` `e` `i` `o` `u` `ə` `ia` |
| `coda` | `str` | 韵尾：空、`j` `w` `r` `m` `n` `ŋ`、入声 `p` `t` `k` `wk` |
| `tone` | `str` | `平` / `上` / `去` / `入` |
| `tone_marker` | `str` | 原始声调标记：`""`、`ʔ`、`h`、`s`、`ps` |

声调与标记：平声无标记；上声 `ʔ`；去声 `h`（来自 *-ks）、`s`（来自 *-ts/*-ps）、
`ps`（只出现在 `əps`）；入声无标记，由 `p`/`t`/`k`/`wk` 韵尾判断。

切分约定：

- **咽化**：`ˤ` 与严格的 RTR 写法 `◌̙`（U+0319）都接受，可以写在声母后
  （`pˤa`），也可以写在元音上（`pa̙`）。
- **-r-**：只指声母之后的 `r`。因此 `sra` 切成 `s` + `-r-` + `a`
  （生母在《音節表》第 3 行写作 `sr`，实际拟音中它是 `s` + 三等 `-r-`）。
- **`C.r`**：这是一个整体符号（表头作“來(~非來)”），不拆成 `C` + `r`。
- **韵尾**：`kʷ` 只是 `wk` 的另一种写法，输出统一规范成 `wk`。

## `mc_initials`

### 用法

只接受 `Syllable`，返回一个中古声母：

```python
>>> from pboc_tanyu import mc_initials, parse_syllable
>>> mc_initials(parse_syllable("tˤa"))    # *t' > 端
'端'
>>> mc_initials(parse_syllable("ta"))     # *t > 章
'章'
>>> mc_initials(parse_syllable("ke"))     # 前元音三等，k > 章
'章'
>>> mc_initials(parse_syllable("ŋe"))     # 前元音三等，ŋ > 日
'日'
>>> mc_initials(parse_syllable("n̥ˤar"))  # 漢、嘆：东部方言 > 透
'透'
```

传裸声母或 IPA 字符串会报 `TypeError`：

```python
>>> mc_initials("ta")
Traceback (most recent call last):
    ...
TypeError: syllable 必须是 parse_syllable 返回的 Syllable，而不是 str
```

### 推导规则

记号：`ˤ` = 非三等（咽化），`r` = 带 -r-。

#### 1. 由 ˤ / -r- 决定的基本结果

| 系 | 条件 | 中古声母 |
| --- | --- | --- |
| P | `p` / `pʰ` / `b` | 幫 / 滂 / 並 |
| M | `m` / `m̥` | 明 / 曉 |
| T | `t`：`ˤ` 无 r / 有 r / 无 ˤ 无 r | 端 / 知 / 章 |
| T | `tʰ`：同上 | 透 / 徹 / 昌 |
| T | `d`：同上 | 定 / 澄 / 常 |
| TS | `ts` / `tsʰ` / `dz`：无 r / 有 r | 精清從 / 莊初崇 |
| S | `s`：无 r / 有 r | 心 / 生 |
| N | `n`：`ˤ` 无 r / 有 r / 无 ˤ 无 r | 泥 / 娘 / 日 |
| L | `l`：`ˤ` 无 r / 有 r / 无 ˤ 无 r | 定 / 澄 / 以 |
| R | `r` / `r̥` | 來 / 見下 |
| K | `k` / `kʰ` | 見 / 溪 |
| K | `g`、`gw`：有 ˤ / 无 ˤ | 匣 / 羣 |
| Ŋ | `ŋ` / `ŋw` | 疑 / 疑 |
| Q | `ʔ` / `ʔw` | 影 / 影 |
| 其他 | `st` / `C.r` / `j` / `kj` / `kʰj` / `kw` / `kʰw` / `sj` | 書 / 來 / 以 / 見 / 溪 / 見 / 溪 / 邪 |

#### 2. 前元音的颚化

前元音 `e`、`i`、`ia` 会让牙喉音声母颚化。条件是**三等、无 -r-**：

| 声母 | 颚化条件 | 颚化结果 | 否则 |
| --- | --- | --- | --- |
| `k` | 前元音 | 章 | 見 |
| `g` | 前元音 | 常 | 羣（有 ˤ 则匣） |
| `ŋ` | 前元音 | 日 | 疑 |
| `h` | 前元音 | 書 | 曉 |

例如 `ke`、`ki`、`ket`、`kiw` 都 > 章；`ge`、`gin` > 常；`ŋe` > 日；`hi` > 書。
《小韻表》里 `k` 的 `kan`、`keŋh`、`ket`、`kinʔ`、`kit`、`kiw`、`kiwʔ` 和
`g` 的 `ge`、`geŋ`、`geŋʔ`、`gew`、`gi`、`giw` 等不合这条统一规则，
当作零星例外，不再为它们加韵尾条件。

#### 3. 清响音：东部方言标准

清响音按**东部方言**（[Nulll《汉代方言区》](https://www.zhihu.com/question/475417874/answer/2024442059)、
[汉代音系](https://zh.wikipedia.org/zh-cn/%E6%BC%A2%E4%BB%A3%E9%9F%B3%E7%B3%BB)）：

- 东部：*n̥-、*l̥-（三等）> 書，*r̥-（三等）> 徹；非三等的 *n̥ˤ-、*l̥ˤ-、*r̥ˤ- > 透。
- 西部：清响音一律 > 曉。本包不取曉。

| 声母 | 规则 |
| --- | --- |
| `n̥` | r → 徹；ˤ → 透；-m 尾 → 書；e/o 元音（-p 尾除外）→ 心；平声 → 心；其余 → 書 |
| `l̥` | r → 徹；ˤ → 透；其余 → 書 |
| `r̥` | ˤ 且非 a 元音 → 透；其余 → 徹 |
| `ŋ̊` | ˤr：a 元音 → 生，否则透；r → 生；非 ˤ 前元音 → 書；其余 → 曉 |
| `ẘ` | 非 ˤ 且（-r 尾或 -s 尾的 a/e）→ 心；其余 → 曉 |

#### 4. 其余多对一

| 声母 | 规则 |
| --- | --- |
| `sl` | 有 ˤ → 心；前元音 → 心，但 `ia` 去声 → 邪；其余 → 邪 |
| `ml` / `mj` | 之部（`ə` 开音节）平声、上声 → 俟；其余 → 船 |
| `j̊` | `-ŋ`/`-k` 尾的 ə/u，或 `-n` 尾去声 → 曉；其余 → 昌 |
| `w` | 有 ˤ → 匣；有 r → 云；前元音 → 去声邪、否则以；其余 → 云 |

规则主要依据知乎《上古-中古音类源流略说》（[p/567955454](https://zhuanlan.zhihu.com/p/567955454)），
并参考《论上古汉语的L系兼论W系》（[p/457736544](https://zhuanlan.zhihu.com/p/457736544)）、
《谐声W系中以母、邪母部分的条件分化可能》（[p/430534985](https://zhuanlan.zhihu.com/p/430534985)）、
《谈谈上古汉语的N系心书母》（[p/495897344](https://zhuanlan.zhihu.com/p/495897344)）。

### 效果

对《小韻表》4034 条有中古声母的音节：

- **3983 条正确，准确率 98.7%**；
- 51 条与《小韻表》的 `推導音韻地位` 不同。

| 声母 | 错误数 | 说明 |
| --- | --- | --- |
| `l̥` | 8 | 6 条心母、2 条西部曉母 |
| `sl` | 7 | 心/邪残留（`slak`、`slat`、`sləs`、`slip` 等） |
| `g` | 7 | `gˤrak` 見，另有 6 条前元音仍羣 |
| `k` | 7 | `kan` 章，另有 6 条前元音仍見 |
| `ŋ̊` | 4 | 4 条心母 |
| `ŋ` | 3 | 2 条羣母例外、1 条 `ŋes` 疑母 |
| `n̥` | 3 | 3 条西部曉母（`n̥ˤu` 薅、`n̥ˤuʔ` 好、`n̥ˤuh` 好） |
| `n` | 2 | `n`+r 例外入日母（`nraŋ`、`nrəm`） |
| `tʰ` | 2 | `tʰˤaj` 定、`tʰˤəp` 端 |
| 其他 | 8 | `p`、`b`、`ts`、`s`、`l`、`kʰ`、`sj`、`ʔw` 各 1 条 |

其中 5 条是**西部方言读法**（`n̥ˤu` 系列、`l̥oj` 墮隋綏隳、`l̥ut` 怴），
按东部标准本就该与《小韻表》的曉母不同。其余 46 条是统一规则带来的零星例外、
词汇扩散或前缀残留。

这 51 条就是目前单值推导与《小韻表》`推導音韻地位` 不一致的全部音节；
完整名单（含 IPA、音类、规则值与表值）见 [mismatches.tsv](mismatches.tsv)。
函数本身已经没有多解输出：4036 条全部返回单值。

### 已知边界

- 只接受 `Syllable`，不再接受裸声母或 IPA 字符串；只给声母时请先
  自己指定 ˤ / -r- 等条件，或直接用 `parse_syllable`。
- 返回值是**单值**：数据本身多解时取规则给出的常规结果，因此会有上表
  约 1.3% 的例外。
- 只处理 IPA 列；工作簿里的 ASCII 拼音列（`paq`、`pah`、`tsh'ymq` 等）不在范围内。
- 本包只做切分、声母推导和等第推导，不推断完整的中古音韵地位（下一步）。

## `mc_grade`

给定 `Syllable`，返回切韵等第 1–4：

```python
>>> from pboc_tanyu import mc_grade, parse_syllable
>>> mc_grade(parse_syllable("ta"))
3
>>> mc_grade(parse_syllable("tˤa"))
1
>>> mc_grade(parse_syllable("tˤra"))
2
>>> mc_grade(parse_syllable("tˤe"))
4
>>> mc_grade(parse_syllable("tˤəj"))
4
>>> mc_grade(parse_syllable("pˤəj"))
1
```

规则：

- **没有咽化 ˤ** → 三等（带不带 -r- 都是三等）；
- **有 ˤ、有 -r-** → 二等；
- **有 ˤ、无 -r-**：
  - 主元音 `e` / `i` / `ia` → 四等；
  - 主元音 `ə`，声母是锐音（`t`、`tʰ`、`d`、`n`、`ts`、`tsʰ`、`dz`、`s`、`l`、`l̥`、`sl`、`r`），
    且韵尾为 `-j` / `-n` / `-t` 或去声 `-s`（不含 `-ps`）→ 四等；
  - 其余（`a` / `o` / `u` / `ə`，或 `ə` 在钝音后）→ 一等。

对《小韻表》4034 条：**3985 条正确（98.8%）**，49 条与表中的等不同。
主要例外：

| 类别 | 条数 | 说明 |
| --- | --- | --- |
| ˤr + o | 16 | 尤部锐音作三等、侯部牙喉音作一等，不按二等 |
| 无 ˤ + r 的莊組/生母 | 10 | 表中作二等（`tsramʔ`、`sroŋ` 等） |
| 无 ˤ 无 r 的 `kj`/`kʰj` | 7 | 表中作一等（`kjoŋ`、`kjunʔ` 等） |
| 其他 | 16 | `ʔwˤa`、`r̥ˤas`、`kʰeŋh`、`lˤuk` 等零星例外 |

完整名单见 [grade_mismatches.tsv](grade_mismatches.tsv)。

## `mc_rhyme`

给定 `Syllable`，返回切韵开合与韵：

```python
>>> from pboc_tanyu import mc_rhyme, parse_syllable
>>> mc_rhyme(parse_syllable("tˤa"))
('合', '模')
>>> mc_rhyme(parse_syllable("ta"))
('開', '魚')
>>> mc_rhyme(parse_syllable("tˤe"))
('開', '齊')
>>> mc_rhyme(parse_syllable("kwa"))
('合', '虞')
>>> mc_rhyme(parse_syllable("tˤak"))
('開', '鐸')
```

韵目以《切韵》为准：平/上/去用平声韵目，入声用入声韵目；
寒合口作桓、歌合口作戈、真合口作諄。

这个映射很不整齐（《源流略说》也明确说“具体的各韵部各等演化可以自己列个表”），
所以按七个主元音拆成七组小表：

- `BASE[vowel][(ˤ, -r-, 有效韵尾)]`：该元音在 ˤ / -r- / 韵尾下的默认 `(開合, 韵)`；
- `OVERRIDES[vowel][(ˤ, -r-, 有效韵尾, 声母类型, 是否合口化声母)]`：
  按声母类型修正的条目；
- 声母类型：唇、舌頭、舌上、齒頭、莊、章、牙、喉、來、日、以；
- 有效韵尾：去声的 `-s`/`-ps` 记为 `s`，其余仍用 IPA 韵尾；
- `is_w`：`kw`、`kʰw`、`gw`、`ŋw`、`ʔw`、`w`、`ẘ` 这类合口化声母。

规则表共 **221 条默认 + 273 条修正**，都在 `_rhyme_rules.py` 里，按元音分成
七组。对《小韻表》4034 条音节，**3977 条一致（98.6%）**，57 条例外（如
`tˤa` 的 模/虞、陽部的 陽/庚、元部的 元/仙 等）见
[rhyme_exceptions.tsv](rhyme_exceptions.tsv)。这比逐条查表小得多，也留出了
以后继续归纳的空间。

## 数据来源

- 粗对照取自工作簿 `dict.xlsx` 的《音節表》第 2、3 行（表内版本 **26.11.21**）。
- 解析规则与分化规则用《小韻表》4036 条音节的 IPA、聲、等、韻、尾、調六列反推并全量校验。
- 开合/韵规则由《小韻表》的 `推導音韻地位` 归纳成七组小表，内嵌为 `_rhyme_rules.py`；运行时不依赖 Excel。
- 清响音的方言取舍见 [Nulll《汉代方言区》](https://www.zhihu.com/question/475417874/answer/2024442059)
  与 [汉代音系](https://zh.wikipedia.org/zh-cn/%E6%BC%A2%E4%BB%A3%E9%9F%B3%E7%B3%BB)。

## 开发

```bash
uv sync --group dev          # 推荐
# 或者
pip install -e . && pip install pytest openpyxl
pytest
```

`tests/test_workbook.py` 会在仓库根目录存在 `dict.xlsx` 且安装了 `openpyxl` 时，
对 4036 条音节和推导准确率做全量校验；否则自动跳过。
