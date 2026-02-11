"""
Generate table images for the NFL Draft ROI article
Extracts table data from source and creates PNG images
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.table_image_generator import TableImageGenerator


def main():
    """Generate all table images for the NFL Draft ROI article"""

    generator = TableImageGenerator()
    output_dir = 'articles/nfl-draft-roi'

    # Table 1: Average Value Score by Draft Round
    print("Generating Table 1: Average Value Score by Draft Round...")
    headers_1 = ['Draft Round', 'Avg Value Score', 'Sample Size', '% Bargains']
    rows_1 = [
        ['Round 1', '+0.36', '568', '3.3%'],
        ['Round 2', '+0.51', '610', '4.9%'],
        ['Round 3', '+0.47', '556', '4.1%'],
        ['Round 4', '+0.34', '508', '2.4%'],
        ['Round 5', '+0.32', '445', '2.0%'],
        ['Round 6', '+0.26', '403', '1.7%'],
        ['Round 7', '+0.15', '567', '0.9%'],
    ]
    generator.create_table_image(
        headers_1, rows_1,
        f'{output_dir}/table_1_avg_value_by_round.png',
        title='Average Value Score by Draft Round'
    )

    # Table 2: Top 5 Draft Sweet Spots
    print("Generating Table 2: Top 5 Draft Sweet Spots...")
    headers_2 = ['Position', 'Round', 'Avg Value Score', 'Sample Size', 'Notable Examples']
    rows_2 = [
        ['QB', '5', '+0.62', '16', 'Brock Purdy, Russell Wilson, Kirk Cousins'],
        ['DB', '3', '+0.60', '92', 'Multiple Pro Bowlers'],
        ['DB', '2', '+0.60', '146', 'Consistent performers'],
        ['TE', '2', '+0.58', '73', 'Travis Kelce, Mark Andrews'],
        ['QB', '2', '+0.56', '16', 'Derek Carr, Jimmy Garoppolo'],
    ]
    generator.create_table_image(
        headers_2, rows_2,
        f'{output_dir}/table_2_top_sweet_spots.png',
        title='Top 5 Draft Sweet Spots'
    )

    # Table 3: Value Score by Position (Round 1 Only)
    print("Generating Table 3: Value Score by Position (Round 1 Only)...")
    headers_3 = ['Position', 'Avg Value Score', 'Sample Size']
    rows_3 = [
        ['QB', '+0.52', '105'],
        ['WR', '+0.45', '89'],
        ['DL', '+0.41', '67'],
        ['TE', '+0.38', '12'],
        ['LB', '+0.21', '53'],
        ['OL', '+0.06', '13'],
        ['DB', '+0.04', '78'],
        ['RB', '+0.02', '52'],
    ]
    generator.create_table_image(
        headers_3, rows_3,
        f'{output_dir}/table_3_value_by_position_round1.png',
        title='Value Score by Position (Round 1 Only)'
    )

    # Table 4: DB Value by Draft Round
    print("Generating Table 4: DB Value by Draft Round...")
    headers_4 = ['Round', 'Avg Value Score', 'Sample Size']
    rows_4 = [
        ['Round 1', '+0.04', '78'],
        ['Round 2', '+0.60', '146'],
        ['Round 3', '+0.60', '92'],
        ['Round 4', '+0.48', '79'],
        ['Round 5', '+0.42', '67'],
    ]
    generator.create_table_image(
        headers_4, rows_4,
        f'{output_dir}/table_4_db_value_by_round.png',
        title='DB Value by Draft Round'
    )

    # Table 5: Top 10 Late-Round Draft Steals
    print("Generating Table 5: Top 10 Late-Round Draft Steals...")
    headers_5 = ['Player', 'Position', 'Year', 'Round', 'Pick #', 'Value Score']
    rows_5 = [
        ['Justin Madubuike', 'DL', '2020', '3', '71', '+3.95'],
        ['Kerby Joseph', 'DB', '2022', '4', '97', '+3.40'],
        ['Jordan Reed', 'TE', '2013', '3', '85', '+3.29'],
        ['Amon-Ra St. Brown', 'WR', '2021', '4', '112', '+3.12'],
        ['Terrel Bernard', 'LB', '2022', '3', '89', '+2.90'],
        ['Tyreek Hill', 'WR', '2016', '5', '165', '+2.73'],
        ['Damontae Kazee', 'DB', '2017', '5', '149', '+2.70'],
        ['George Kittle', 'TE', '2017', '5', '146', '+2.68'],
        ['Dalton Schultz', 'TE', '2018', '4', '137', '+2.66'],
        ['Joe Schobert', 'LB', '2016', '4', '99', '+2.63'],
    ]
    generator.create_table_image(
        headers_5, rows_5,
        f'{output_dir}/table_5_late_round_steals.png',
        title='Top 10 Late-Round Draft Steals (2015-2024)'
    )

    # Table 6: Biggest First-Round "Busts" (By Value Score)
    print("Generating Table 6: Biggest First-Round Busts...")
    headers_6 = ['Player', 'Position', 'Pick #', 'Value Score']
    rows_6 = [
        ['Christian McCaffrey', 'RB', '8', '-4.64'],
        ['Ezekiel Elliott', 'RB', '4', '-3.07'],
        ['Jaylen Waddle', 'WR', '6', '-2.74'],
        ['Vita Vea', 'DL', '12', '-2.52'],
        ['Penei Sewell', 'OL', '7', '-2.25'],
    ]
    generator.create_table_image(
        headers_6, rows_6,
        f'{output_dir}/table_6_first_round_busts.png',
        title='Biggest First-Round "Busts" (By Value Score)'
    )

    # Table 7: Position-Specific Draft Strategy
    # Note: This table already has a working image in the article, but we'll create
    # a text version that matches the style for consistency
    print("Generating Table 7: Position-Specific Draft Strategy...")
    headers_7 = ['Position', 'Best Rounds', 'Avoid', 'Notes']
    rows_7 = [
        ['QB', '1-2, 5', '3-4, 6', 'Round 5 is elite value if willing to develop'],
        ['RB', '2-3', '1', 'Never justify RBs in Round 1 unless generational'],
        ['WR', '2-4', '7', 'Round 2 WRs (+0.55) are consistent value'],
        ['TE', '2, 5', '1', 'Round 5 TEs (+0.53) punch above weight'],
        ['OL', '2-3', '1', 'First-round OL barely break even (+0.06)'],
        ['DL', '2-4', '7', 'Solid value across middle rounds'],
        ['LB', '3-4', '1, 7', 'Late-round LBs underperform'],
        ['DB', '2-3', '1', 'Round 1 DBs (+0.04) are massive disappointments'],
    ]
    generator.create_table_image(
        headers_7, rows_7,
        f'{output_dir}/table_7_position_strategy.png',
        title='Position-Specific Draft Strategy'
    )

    print(f"\n[SUCCESS] All 7 table images generated successfully!")
    print(f"[INFO] Images saved to: {output_dir}/")
    print("\nGenerated files:")
    for i in range(1, 8):
        print(f"  - table_{i}_*.png")


if __name__ == '__main__':
    main()
