LMOP additional research - 6 October 2026

Extract, then open LMOP_Explorer_Final.html in Chrome or Edge.
The entire application works offline with no installation. It contains the
original 2,641 landfill records plus geographic diagnostics and a downloadable
757-record public-source verification queue (the Record review section). The
research results are under Research and provenance. Queue buckets are
verification categories, not investment rankings, actual feasibility or
methane reduction estimates. Published copy:
https://chesleyguo.github.io/landfill_dashboard/LMOP_Explorer_Final.html

Explorer features (interface update, 21 October 2026)
-----------------------------------------------------
The underlying records, model results and review queue are unchanged; only the
page interface was extended.
- Layout: a bar that stays at the top while scrolling shows how many sites
  are selected and which filters are on, with Edit filters, Reset and Copy
  view link, plus links to each section (Filters, Overview, Map, Charts,
  Compare, Records, Review, Research); the section in view is highlighted.
  Five common filters and search are always shown; the rest are under
  "More filters" (which shows how many are active). Press / to jump to search.
- Records table: every column sorts (select a heading: first click high-to-low
  for numbers, A-Z for text; again to reverse; a third time restores the
  original order). Missing values always sort last. A Waste year column was
  added. Choose 20/40/100/250 rows per page or type a page number.
- CSV export follows the current sort, and records the sort in its
  Selection Filters column. Both exports sit next to the records table
  and include every selected record, not only the visible page: "Table
  columns" (the table's columns plus Landfill ID and review fields) and "All
  source fields" (all 16 source fields).
- Shareable views: filters, sort, page, chart and comparison choices are kept
  in the address after "#" (e.g. LMOP_Explorer_Final.html#state=CA&sort=waste-desc).
  "Copy view link" copies it. On the published site the link opens the same
  view directly; from a local copy it contains a local file path, so a
  recipient appends the "#..." part to the address of their own copy.
- Active filters appear as removable tags under the filter panel.
- Map: one panel with two views, Sites (see Landfill locations below) and
  State rates.
- State rates: a schematic tile map (equal tiles, not geographic
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
- More filters: County (after choosing a state), Record review (the 757-site
  queue, each review bucket, sites outside the queue, or the four
  public-source spot checks) and Project status checkboxes (Operational,
  Construction, Planned, Candidate, Future Potential, Low Potential, Shutdown,
  Unknown; a site matches if it carries any selected status). "Comparison
  within selection" can also group by county.
- Project status records chart: share of sites carrying each status under the
  other filters (a site can carry several, so bars do not sum to 100%);
  select a bar to filter. Waste data year chart: how old each waste value is.
- Records table: review-bucket and spot-check badges, and the full project
  status set under the energy record. Table columns export includes county,
  project statuses, review bucket and spot-check flag.
- Site details: Previous/Next through the current order (arrow keys work),
  the record's review question, public-source check findings and limits,
  operational parent projects with links to other landfills supplying the same
  project, an EPA source link, and the seven retrospective leave-state-out
  model scores. Scores describe the September 2024 register only (not
  feasibility, priority or a forecast), are shown rounded, and are
  deliberately not sortable; Unknown-only sites have none.
- Additional research: a forest plot of the four paired AP differences, a
  per-state fold chart (AP against prevalence, with the pooled AP), and a
  threshold explorer on the 510 held-out sites (precision, recall, flagged
  sites and false positives at any threshold; 0.5 and the training-selected
  0.338 reproduce the published 62/27 and 113/55). The explorer uses holdout
  labels for illustration and must not be used to pick a threshold.
- The Record review section has "Show these 757 records in the table".
- Groups in "Comparison within selection" (status, ownership, state, county)
  can be selected to filter by them; select again to clear.
- The page embeds compact copies of reference_results/geographic_predictions.csv
  (scores in thousandths), public_reference/holdout_predictions.csv,
  public_reference/operational_project_site_links.csv and
  reference_results/public_status_spot_checks.csv (about 110 KB), plus the
  map data (about 310 KB): state outlines from U.S. Census Bureau
  cartographic boundaries (2017) via us-atlas 3.0.1 states-albers-10m.json
  (ISC license, SHA256 6e7bb086a3c791490361968a3094f377f7726c5d0c4900fec03cc42db2305a3d)
  and site positions projected from public_reference/landfill_locations.csv.
- public_reference/landfill_locations.csv (latitude, longitude, city, GHGRP
  ID) is extracted from the official landfill file, after its hash is checked:
    python scripts/extract_landfill_locations.py path/to/landfilllmopdata.xlsx
- Landfill locations: a point map of the selected sites (Albers USA; Alaska,
  Hawaii, Puerto Rico, Guam and the U.S. Virgin Islands as insets), colored
  by energy record and optionally sized by waste in place. It zooms to the
  selected state or county. 2,322 of 2,641 sites are mapped: 318 have no
  coordinates in the source, and Pine Tree Landfill (ID 2259, Maine) has a
  source longitude of -98.8695, which places it outside Maine, so it is not
  mapped and the source value is left uncorrected. Site details add city,
  GHGRP facility ID (1,332 sites; the key for a future join to EPA GHGRP
  emissions), coordinates and the five nearest landfills.
- Energy projects (from the September 2024 project file lmopdata.xlsx, hash
  a5c8bea2..., the same release as the landfill file): a chart of Operational
  projects at the selected landfills by start period and type (electricity,
  direct use, renewable natural gas), with totals for rated MW, LFG flow and
  EPA-estimated current-year emission reductions (estimates, not
  measurements). Each site's details list its project rows. A new "Operational
  project type" filter is under More filters. 652 Operational projects
  (including expansions) at 488 landfills, 542 parent projects; this agrees
  with public_reference/operational_project_site_links.csv.
- Airborne methane observations: Cusworth et al. (2024), "Quantifying methane
  emissions from United States landfills", Science 383:1499-1504
  (doi:10.1126/science.adi7735); data published by EPA ORD
  (doi:10.23719/1531980, science.adi7735_data_s1.xlsx, SHA256
  a0e78827cb0fe3f045b767dbaad93c0e66883c480ca17bb3bc498c6b324ff30b; EPA
  public-domain data license). All 107 landfills in its time-averaged source
  list join to exactly one LMOP landfill by GHGRP ID (18 states, 2016-2022).
  The chart shows each observed landfill's average emission rate (kg CH4/h,
  log scale, optionally per million short tons of waste in place) by energy
  record, with medians. These are airborne snapshots of large landfills, not
  annual totals, and sites with projects tend to be larger, so differences are
  not effects of projects. Values are copied as published: 11 listed
  landfills have no average rate, and 40 plumes under 7 GHGRP IDs (one,
  "7837", malformed) are not in the source list; neither is corrected.
  Details show the rate, uncertainty, days flown, plume dates and the reported
  GHGRP value as published (tCO2e, not converted). Filter: "Airborne methane
  data" under More filters.
- public_reference/landfill_projects.csv and
  public_reference/airborne_methane_cusworth2024.csv are produced, after both
  hashes are checked, by:
    python scripts/extract_project_and_airborne_data.py lmopdata.xlsx science.adi7735_data_s1.xlsx
- My review workbench (Record review section and each site's details): record
  a result (confirmed as recorded, discrepancy found, could not determine),
  notes and an evidence link for any site, step to the next unreviewed record,
  filter by "My review", and export (CSV) or back up / restore (JSON).
  Reviews are stored only in the browser on that device; they are never
  uploaded and other visitors cannot see them.
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
Prepared with Codex and Claude assistance.

Final extension: four public-source status examples with dated/undated identity limits. Historical model targets remain unchanged. Public webpages/PDF binaries are not bundled; source URLs and paraphrased evidence are retained.
