# Build verification

2026-11-08: Built successfully from the included 2.2.8 TrueType outline master using the pinned dependencies. All glyph outlines and character mappings match the published 2.2.9 TTF. Built-in name, metrics and weight-axis assertions passed. Measured 6,977 Han/Latin/digit glyphs; median regular stroke width: 31.86 design units.

2026-11-09: Rebuilt 2.2.10 from the included master. The glyph, variation, character mapping, metrics, axis and naming tables match the release font. Only the outlines of 深 and 班 changed.

2.2.11: Rebuilt from the included master. Compared with 2.2.10, only 探 and 班 changed in the glyph and variation tables. Character coverage and advance widths match. Checked 400, 500 and 650 weight instances.
