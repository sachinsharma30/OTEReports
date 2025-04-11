import pandas as pd
from weasyprint import HTML

# === Utility function for styling cells ===
def style_cell(val, col):
    try:
        value = float(str(val).replace('%', '').replace(',', '.'))
    except:
        return ''
    '''if col == "2P%":
        if value > 50:
            return 'background-color: lightgreen;'
        elif 45 <= value <= 50:
            return 'background-color: yellow;'
        else:
            return 'background-color: lightcoral;'
    if col == "3P%":
        if value > 35:
            return 'background-color: lightgreen;'
        elif 30 <= value <= 35:
            return 'background-color: yellow;'
        else:
            return 'background-color: lightcoral;'
    if col == "FG%":
        if value > 45:
            return 'background-color: lightgreen;'
        elif 40 <= value <= 45:
            return 'background-color: yellow;'
        else:
            return 'background-color: lightcoral;' '''
    if col == "C-RAM":
        if value >= 10:
            return 'background-color: gold;'
        elif 8.5 <= value < 10:
            return 'background-color: silver;'
        elif 7.0 <= value < 8.5:
            return 'background-color: #cd7f32;'
    return ''

# === Styling functions ===
def apply_styles(df):
    return df.style \
        .format(precision=1) \
        .applymap(lambda val: style_cell(val, "2P%"), subset=df.columns.intersection(["2P%"])) \
        .applymap(lambda val: style_cell(val, "3P%"), subset=df.columns.intersection(["3P%"])) \
        .applymap(lambda val: style_cell(val, "FG%"), subset=df.columns.intersection(["FG%"])) \
        .applymap(lambda val: style_cell(val, "C-RAM"), subset=df.columns.intersection(["C-RAM"])) \
        .set_table_attributes('class="report-table" border="0"')

def apply_no_style(df):
    return df.style.format(precision=1).set_table_attributes('class="report-table" border="0"')

# === Superheader injectors ===
def inject_headers(table_html, groups):
    import re
    parts = table_html.split('<thead>')
    head_parts = parts[1].split('</thead>')
    thead_content = head_parts[0]
    headers = re.findall(r'<th .*?>(.*?)</th>', thead_content)
    new_row = '<tr>'
    for label, cols in groups:
        colspan = sum(col in headers for col in cols)
        if colspan > 0:
            new_row += f'<th colspan="{colspan}" class="super-header">{label}</th>'
    new_row += '</tr>'
    new_thead = thead_content.replace('<tr>', new_row + '<tr>', 1)
    return parts[0] + '<thead>' + new_thead + '</thead>' + head_parts[1]

def inject_player_super_headers(table_html):
    import re
    parts = table_html.split('<thead>')
    head_parts = parts[1].split('</thead>')
    thead_content = head_parts[0]
    headers = re.findall(r'<th .*?>(.*?)</th>', thead_content)
    try:
        fd_index = headers.index('FD')
        two_pm_index = headers.index('2PM')
    except ValueError:
        return table_html
    box_score_cols = fd_index + 1
    shooting_cols = len(headers) - two_pm_index
    new_row = f'''
    <tr>
        <th colspan="{box_score_cols}" class="super-header">BOX SCORE STATS</th>
        <th colspan="{shooting_cols}" class="super-header">SHOOTING</th>
    </tr>
    '''
    new_thead = thead_content.replace('<tr>', new_row + '<tr>', 1)
    return parts[0] + '<thead>' + new_thead + '</thead>' + head_parts[1]

def inject_team_super_headers(table_html):
    groups = [
        ("BOX SCORE STATS", ['Team', 'PTS', 'ORB', 'DRB', 'TRB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'FD']),
        ("SHOOTING", ['2PM', '2PA', '2P%', '3PM', '3PA', '3P%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '+/-'])
    ]
    return inject_headers(table_html, groups)

def inject_advanced_super_headers(table_html):
    groups = [
        ("SHOOTING", ['Player', 'TSA', 'TS%', '3PAr', 'FTAr']),
        ("SHOT CREATION", ['AST%', 'TO%', 'USG%']),
        ("REBOUNDING", ['ORB%', 'DRB%']),
        ("DEFENSE", ['STL%', 'BLK%']),
        ("CEREBRO RAM", ['RAM', 'C-RAM']),
        ("CEREBRO 5 METRIC SUITE", ['PSP', '3PE', 'FGS', 'ATR', 'DSI'])
    ]
    return inject_headers(table_html, groups)

def inject_team_advanced_super_headers(table_html):
    groups = [
        ("EFFICIENCY", ['Team', 'ORTG', 'DRTG', 'Net RTG']),
        ("FOUR FACTORS", ['eFG%', 'TO%', 'ORB%', 'FTAr']),
        ("PLAY STYLE", ['POSS', '3PAr', 'AST%', 'PITP']),
        ("MISC", ['2ND CHANCE PTS', 'FB PTS', 'PTS OF TO', 'BENCH PTS'])
    ]
    return inject_headers(table_html, groups)

def inject_quarter_super_headers(table_html):
    return inject_team_super_headers(table_html)

# === Pandas display settings ===
pd.set_option('display.max_rows', None)

# === Prepare tables ===
def prepare_table(path, header_injector, no_style=False):
    df = pd.read_csv(path)
    if no_style:
        styled = apply_no_style(df).hide(axis="index").to_html()
    else:
        styled = apply_styles(df).hide(axis="index").to_html()
    styled = header_injector(styled)
    return styled

def prepare_basic_table(path):
    df = pd.read_csv(path)
    return df.style.format(precision=1).hide(axis="index").set_table_attributes('class="report-table" border="0"').to_html()

# === Load Data ===
# Page 2
styled_totals = prepare_table('tables/player_totals.csv', inject_player_super_headers)
styled_averages = prepare_table('tables/player_averages.csv', inject_player_super_headers)

# Page 3
styled_per40 = prepare_table('tables/player_per40.csv', inject_player_super_headers)
styled_advanced = prepare_table('tables/player_advanced_stats.csv', inject_advanced_super_headers)

# Page 4 (no styling!)
styled_team_averages = prepare_table('tables/team_averages.csv', inject_team_super_headers, no_style=True)
styled_opp_averages = prepare_table('tables/opp_averages.csv', inject_team_super_headers, no_style=True)
styled_team_advanced = prepare_table('tables/team_advanced_stats.csv', inject_team_advanced_super_headers)
styled_opp_advanced = prepare_table('tables/opp_advanced_stats.csv', inject_team_advanced_super_headers)

# Page 5
styled_win_splits = prepare_table('tables/win_splits.csv', inject_player_super_headers)
styled_loss_splits = prepare_table('tables/loss_splits.csv', inject_player_super_headers)

# Page 6 (no styling!)
styled_quarter_averages = prepare_table('tables/quarter_averages.csv', inject_quarter_super_headers, no_style=True)
styled_quarter_rank = prepare_table('tables/quarter_rank.csv', inject_quarter_super_headers, no_style=True)
styled_bb = prepare_basic_table('tables/bb.csv')
styled_opp_bb = prepare_basic_table('tables/opp_bb.csv')

# === Build full HTML ===
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Team Report - YNG Dreamerz</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <!-- Page 1 -->
    <div class="page">
        <div class="banner"><span class="banner-text">Team Report - YNG Dreamerz</span></div>
        <div class="cover-page">
            <img src="assets/ote_logo.png" alt="OTE Logo">
            <h1>Team Report - YNG Dreamerz</h1>
            <p>2024-11-01 / 2025-02-15</p>
            <p>Team Record: 8 - 12</p>
        </div>
        <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
    </div>

    <!-- Page 2 -->
    <div class="page page-break">
        <div class="banner"><span class="banner-text">Team Report - YNG Dreamerz</span></div>
        <div class="content">
            <h2 class="table-title">Player Totals</h2>{styled_totals}
            <h2 class="table-title">Player Averages</h2>{styled_averages}
        </div>
        <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
    </div>

    <!-- Page 3 -->
    <div class="page page-break">
        <div class="banner"><span class="banner-text">Team Report - YNG Dreamerz</span></div>
        <div class="content">
            <h2 class="table-title">Player Per 40 Minutes</h2>{styled_per40}
            <h2 class="table-title">Player Advanced</h2>{styled_advanced}
        </div>
        <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
    </div>

    <!-- Page 4 -->
    <div class="page page-break">
        <div class="banner"><span class="banner-text">Team Report - YNG Dreamerz</span></div>
        <div class="content">
            <h2 class="table-title">Team Averages</h2>{styled_team_averages}
            <h2 class="table-title">Opponent Averages</h2>{styled_opp_averages}
            <h2 class="table-title">Team Advanced Averages</h2>{styled_team_advanced}
            <h2 class="table-title">Opponent Advanced Averages</h2>{styled_opp_advanced}
        </div>
        <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
    </div>

    <!-- Page 5 -->
    <div class="page page-break">
        <div class="banner"><span class="banner-text">Team Report - YNG Dreamerz</span></div>
        <div class="content">
            <h2 class="table-title">Win Splits</h2>{styled_win_splits}
            <h2 class="table-title">Loss Splits</h2>{styled_loss_splits}
        </div>
        <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
    </div>

    <!-- Page 6 -->
    <div class="page page-break">
        <div class="banner"><span class="banner-text">Team Report - YNG Dreamerz</span></div>
        <div class="content">
            <h2 class="table-title">Team Quarter Averages</h2>{styled_quarter_averages}
            <h2 class="table-title">Team Quarter Rank</h2>{styled_quarter_rank}
            <div class="mini-tables">
                <div class="mini-table"><h2 class="table-title">Big Bonus Breakdown</h2>{styled_bb}</div>
                <div class="mini-table"><h2 class="table-title">Big Bonus Opponent Breakdown</h2>{styled_opp_bb}</div>
            </div>
        </div>
        <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
    </div>

</body>
</html>
"""

# === Generate PDF ===
HTML(string=html_content, base_url='.').write_pdf('report.pdf')
print("✅ PDF generated successfully as report.pdf")
