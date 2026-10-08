# Data review: snapshot 2026-09-26 run 1

Source: `data/snapshots/sephora_ca_2026-09-26_run1_skus.csv.gz`, 8,742 SKUs, 2,570 products, 167 brands.

## 1. Linking minis to full sizes

### Finding the minis
| Signal | Products |
|---|---|
| Mini/travel category (`Mini Size`, `Rollerballs & Travel Size`, `Travel Size & Mini Cologne`) | 209 |
| Name has `mini`, `travel size/spray` or `rollerball` | 244 |
| Category but not name | 3 (tarte eyelash curler, Naked2 Basics palette, Versace "Ovetto Spray") |
| Name but not category | 38 (e.g. Origins, Fenty, Sol de Janeiro minis filed under Skincare/Bath & Body) |

**Use category OR name** (247 products). Category alone misses about 15%.

Minis are almost always separate product codes. Only 3 full-size products carry a mini as a SKU
(e.g. size `"Mini Size Black - 0.13 oz/ 4 mL"`).

### Matching
Within the same brand, normalise names (drop `Mini`, `Travel Spray`, `Rollerball`, `Refillable`,
™/®, stop words; fix `Eu de` -> `Eau de`) and score each full-size candidate by **token coverage**:
the share of the mini's name tokens found in the candidate. Ties are broken by Jaccard similarity.
Plain string similarity (difflib) did worse because full-size names add descriptors
("...with Peptides for Nourishing Hydration").

| Tier | Coverage | Minis | Spot-check precision |
|---|---|---|---|
| all-tokens | 100% | 209 (23 tied) | ~95%, ties need a look |
| likely | 75–99% | 9 | ~75% |
| weak | 50–75% | 9 | ~30% |
| none | <50% | 20 | full size mostly **not in the scrape** (e.g. NARS Climax, amika Soulfood) |

Known false positives, all in the tied or low tiers:
- `Mini Hyaluronic Serum` -> `Darker Skin Tones Hyaluronic Serum`
- `Mini Ambient Lighting Powder` -> `Ambient Strobe Lighting Powder`
- `ROSIE travel spray` -> `ROSIE perfume oil` (different format)
- `Mini Better Than Sex Waterproof Mascara` -> `...Foreplay ... Primer`
- Fragrance minis whose brand sells EDP, EDT and Intense versions

Candidates for review: `mini_link_candidates.csv`. Accept `all-tokens` where `ambiguous == False`
(186 links). Eyeball the other ~60 and keep a small hand-made override table.

Extra checks that would raise precision: the mini's size should be smaller than the full size, and
the same unit family should be used on both sides (mL vs g).

### First pass at unit-price ratios
For 196 confident links with a comparable unit (mL, then g, then oz), comparing mini price per unit
with the full product's cheapest price per unit:

- median **1.79×**, IQR 1.40–2.25×, max 4.5×
- mini cheaper per unit: 6 links, but 3 of those are false links (above). The real ones are
  `lights camera lashes` mascara (0.77×), `Lash Idôle` mascara (0.91×) and `Twilly Tutti` (0.97×).
  Mascara minis are the deals.

## 2. Missing data and errors

| Issue | Rows | Notes |
|---|---|---|
| `size` empty | 307 (3.5%) | mostly `Color` variations (210) and `None` (72) |
| size with numbers but **no unit** | 235 (2.7%) | `1 / 30`, `1.7/50`, `3.3/100`: oz/mL pairs without units |
| size-variation SKUs with no usable size | 173 (2.0%) | these are the ones that matter for unit prices |
| unit-prefixed sizes lost | small | `Mini Size Black - 0.17 oz` loses its oz: the parser needs the number first |
| oz vs g grossly inconsistent | 82 rows, 14 products | Sephora typos: `0.038 oz / 11 g`, `4.5 oz/ 0.158 g`, `21 oz/6 g`, `00.6 oz` |
| oz vs mL off (outside 25–35 mL/oz) | 42 | mostly aerosols/dry shampoo sized by weight oz. Not errors, but don't treat oz as fl oz |
| `price` missing | 6 | |
| `sale_price` present | 102 (1.2%) | |
| `ingredients` missing | 294 (3.4%) | |
| `rating`/`reviews` missing | 14 | new products |
| `brand_name` missing | 4 | |
| `category_name` empty | 2 | BIRTHDAY GIFT sets. Crashes `preprocess` |
| duplicate `sku_id` | 0 | |

Size strings with extra text (`size_info`, 308 rows): `mini`, `Refill`, `x2`/`x5` multipacks,
`fillsizesequence:1`, `Value Size`, duo products (`cream and .14 oz powder`). Multipacks need the
count multiplied in before computing unit prices.

### Pipeline bugs found
`shelf-life preprocess --snapshot ...` crashes on this snapshot:
1. `parse_size` calls `.strip()` on NaN (empty sizes read from CSV come back as float).
2. The category split calls `len()` on NaN (the 2 gift rows).

The db path doesn't hit (1) because SQLite returns `None`.
