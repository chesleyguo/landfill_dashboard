LMOP additional research - 6 October 2026

Extract, then open LMOP_Explorer_Final.html in Chrome or Edge.
The entire application works offline with no installation. It contains the
original 2,641 landfill records plus geographic diagnostics and a downloadable
757-record public-source verification queue. Expand the two Additional research
and Practical record-review sections. Queue buckets are verification categories,
not investment rankings, actual feasibility or methane reduction estimates.

Explorer features (interface update, 21 October 2026)
-----------------------------------------------------
The underlying records, model results and review queue are unchanged; only the
page interface was extended.
- Records table: every column sorts (select a heading: first click high-to-low
  for numbers, A-Z for text; again to reverse; a third time restores the
  original order). Missing values always sort last. A Waste year column was
  added. Choose 20/40/100/250 rows per page or type a page number.
- CSV export follows the current sort, and records the sort in its
  Selection Filters column.
- Shareable views: filters, sort, page, chart and comparison choices are kept
  in the address after "#" (e.g. LMOP_Explorer_Final.html#state=CA&sort=waste-desc).
  "Copy view link" copies it. The link contains a local file path, so a
  recipient appends the "#..." part to the address of their own copy.
- Active filters appear as removable tags under the filter panel.
- States and territories: a schematic tile map (equal tiles, not geographic
  area) colored by Operational record share, active collection share,
  Collection Yes / (Yes + No) or site count. It ignores the State filter so
  states stay comparable; select a tile to filter by that state. Tiles with a
  rate denominator under 10 have a dashed outline.
- Waste in place distribution: log-scale histogram of selected sites, split by
  Operational energy record, with a table view. Sites without a waste value
  are counted but not drawn.
- Compare two groups: choose a dimension (status, ownership, collection, waste
  size, state) and two values to see shares side by side with differences in
  percentage points. Descriptive only, not significance tests or causal effects.
- Theme button: automatic (follows the system), light or dark. The choice is
  stored only in this browser.
- Phones show records as cards with a sort menu. Printing expands all
  collapsed sections and adds a line with print time, filters, sort and view
  link; only the current page of the records table is printed.

Scientific scope
----------------
Seven fixed L2 logistic feature specifications; 53 leave-state/territory-out
folds on 2,325 known-status sites; 316 Unknown-only sites never treated as zero.
The target is recorded Operational status, not actual adoption or emissions.
This is retrospective stress testing of the existing September 2024 register,
not an independent external dataset or temporal forecast. No test-set winner
was selected. Original holdout ablations and paired conditional uncertainty
are secondary analyses. Coverage limits and small geographic folds are retained.

The training-only threshold diagnostic reaches 70.1% training recall, but only
62.4% on the unchanged original holdout. It flags 113 sites, with 55 false
positives, compared with 62 / 27 at threshold 0.5. Not deployment-ready.

Offline scientific reproduction
-------------------------------
Use Python 3.12 with requirements.txt installed, then:
  python scripts/reproduce_lmop_robustness.py
Use a fresh extraction for every run. All packaged file hashes are checked
before analysis, and prior run directories are never overwritten. Public-derived
labels, links and original split/predictions are included, so this supplemental
rerun needs no data downloads. It reproduces all geographic probabilities,
training-selected threshold and paired intervals. Browser automation is not
rerun by the helper; actual browser QA records are included as evidence.
reference_results/browser_qa.json was recorded on 7 October 2026 against the
earlier interface. The embedded data are unchanged, but those checks were not
rerun on, and do not cover, the 21 October interface update.

After editing any packaged file (including this README or the HTML page),
refresh its size and hash in PACKAGE_MANIFEST.json, or the reproduction
helper will stop at the hash check:
  python scripts/update_manifest.py          # update changed entries
  python scripts/update_manifest.py --check  # list mismatches, change nothing
The script only updates files already listed; it never adds or removes entries.

The previous research package separately reran the full source audit from fresh
official XLSX downloads and verified original hashes. This supplement does not
pretend to repeat those downloads. No private sources, mail, credentials, raw
lab data, software environment or entire project archive is included.

Official source release (all September 2024)
------------------------------------------
https://www.epa.gov/system/files/documents/2024-09/landfilllmopdata.xlsx
SHA256 2fc1d72ca9c022fb3ce9225f3b4ae5466b0b9c28b7d7efe7a10d2ac1415a0aa6
https://www.epa.gov/system/files/documents/2024-09/lmopdata.xlsx
SHA256 a5c8bea26e7b5f6ecef247b762bde89b999915504814825a1eac7a1cd9f4ddd3
https://www.epa.gov/system/files/documents/2024-09/opprjslmopdata-aggregated.xlsx
SHA256 dc6b61417de738cb6241408b1f1ab9608e423b2bf26e53da25b9936b9dd88a3c
Definitions and coverage: https://www.epa.gov/lmop/landfill-technical-data
https://www.epa.gov/lmop/landfill-gas-energy-project-data

Mixed years, incomplete recording and uneven Unknown exclusions limit all
inferences. Waste amounts are US short tons. The waste year is not the date
of every status. Public source availability is not asserted to be a CC0 license.
Prepared with Codex assistance for the Alice / Chesley research project.

Final extension: four public-source status examples with dated/undated identity limits. Historical model targets remain unchanged. Public webpages/PDF binaries are not bundled; source URLs and paraphrased evidence are retained.
