import pandas as pd
from weasyprint import HTML
import os

# === Pandas settings ===
pd.set_option('display.max_rows', None)

# === Highlighting function for C-RAM only ===
def style_cell(val, col):
    try:
        value = float(str(val).replace('%', '').replace(',', '.'))
    except:
        return ''
    if col == "C-RAM":
        if value >= 10:
            return 'background-color: gold;'
        elif 8.5 <= value < 10:
            return 'background-color: silver;'
        elif 7.0 <= value < 8.5:
            return 'background-color: #cd7f32;'
    return ''

# === Superheader injection function ===
def inject_superheader(html, groupings):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return html  # Fail-safe

    # Extract all columns
    headers = [th.get_text(strip=True) for th in table.find_all("th")]

    # Create superheader row
    super_tr = soup.new_tag("tr")
    for group_name, columns in groupings:
        span = sum(1 for col in columns if col in headers)
        if span == 0:
            continue
        th = soup.new_tag("th", attrs={"class": "super-header", "colspan": str(span)})
        th.string = group_name
        super_tr.append(th)

    # Insert the new superheader row at the top of the table head
    thead = table.find("thead")
    if thead:
        thead.insert(0, super_tr)

    return str(soup)

# === Prepare individual player table from DataFrame ===
def prepare_player_table(player_name, df, name_column="Name", highlight_cram=False, no_decimals=False, inject_groups=False, reverse_order=False):
    player_df = df[df[name_column] == player_name]

    if player_df.empty:
        return None

    # Drop name column for cleaner display
    player_df = player_df.drop(columns=[name_column])

    # ✅ Reverse the rows if requested
    if reverse_order:
        player_df = player_df.iloc[::-1]

    # Convert numeric columns safely
    player_df = player_df.apply(pd.to_numeric, errors='ignore')

    # Start styling
    styled = player_df.style.hide(axis="index").set_table_attributes('class="report-table" border="0"')

    # Apply formatting
    if no_decimals:
        format_dict = {}
        for col in player_df.columns:
            if player_df[col].dtype in ['float64', 'int64']:
                if "%" in col or "P%" in col or "FG%" in col:
                    format_dict[col] = "{:.1f}%"
                else:
                    format_dict[col] = "{:.0f}"
        styled = styled.format(format_dict)
    else:
        styled = styled.format(precision=1)

    # If C-RAM highlighting requested, apply styling
    if highlight_cram and 'C-RAM' in player_df.columns:
        styled = styled.applymap(lambda val: style_cell(val, "C-RAM"), subset=['C-RAM'])

    html_table = styled.to_html()

    # ✅ Inject superheaders if requested
    if inject_groups:
        groupings = [
            ("SHOOTING", ['Season', 'TSA', 'TS%', '3PAr', 'FTAr']),
            ("SHOT CREATION", ['AST%', 'TO%', 'USG%']),
            ("REBOUNDING", ['ORB%', 'DRB%']),
            ("DEFENSE", ['STL%', 'BLK%']),
            ("CEREBRO RAM", ['RAM', 'C-RAM']),
            ("CEREBRO 5 METRIC SUITE", ['PSP', '3PE', 'FGS', 'ATR', 'DSI'])
        ]
        html_table = inject_superheader(html_table, groupings)

    return html_table

# === Build full HTML for player ===
def build_html(player_name, totals_html, averages_html, per40_html, advanced_html, game_logs_current_html, game_logs_previous_html):
    # Prepare page 2 (only if previous seasons exist)
    game_logs_previous_section = ""
    if game_logs_previous_html:
        game_logs_previous_section = f"""
        <!-- Page 2: Previous Season Game Logs -->
        <div class="page page-break">
            <div class="banner"><span class="banner-text">Player Report - {player_name}</span></div>
            <div class="content">
                <h2 class="table-title">Game Logs: Previous Seasons</h2>
                {game_logs_previous_html}
            </div>
            <img src="assets/ote_logo.png" class="ote-logo" alt="OTE Logo">
            <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
        </div>
        """

    # Main HTML structure
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Player Report - {player_name}</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>

        <!-- Page 1: Player Summary + 2024–25 Game Logs -->
        <div class="page page-break">
            <div class="banner"><span class="banner-text">Player Report - {player_name}</span></div>
            <div class="content">
                <h2 class="table-title">Traditional Stats Totals</h2>
                {totals_html}
                <h2 class="table-title">Per Game Stats</h2>
                {averages_html}
                <h2 class="table-title">Per 40-Minute Stats</h2>
                {per40_html}
                <h2 class="table-title">Advanced Stats</h2>
                {advanced_html}
                <h2 class="table-title">Game Logs: 2024–2025 Season</h2>
                {game_logs_current_html}
            </div>
            <img src="assets/ote_logo.png" class="ote-logo" alt="OTE Logo">
            <img src="assets/cerebro_logo.png" class="cerebro-logo" alt="Cerebro Logo">
        </div>

        {game_logs_previous_section}

    </body>
    </html>
    """

# === Read datasets once ===
df_totals = pd.read_csv('tables/player_totals.csv')
df_averages = pd.read_csv('tables/player_averages.csv')
df_per40 = pd.read_csv('tables/player_per40.csv')
df_advanced = pd.read_csv('tables/player_advanced_stats.csv')
df_game_logs = pd.read_csv('tables/player_game_logs.csv')

# Get list of unique player names from totals
player_names = df_totals['Name'].unique()

# Output directory
output_dir = 'player_reports'
os.makedirs(output_dir, exist_ok=True)

# Generate report for each player
for player_name in player_names:
    totals_html = prepare_player_table(player_name, df_totals, name_column="Name", reverse_order=True)
    averages_html = prepare_player_table(player_name, df_averages, name_column="Name", reverse_order=True)
    per40_html = prepare_player_table(player_name, df_per40, name_column="Name", reverse_order=True)
    advanced_html = prepare_player_table(player_name, df_advanced, name_column="Player", highlight_cram=True, inject_groups=True)

    # Split game logs
    df_player_game_logs = df_game_logs[df_game_logs["Name"] == player_name]
    df_current_season = df_player_game_logs[df_player_game_logs["Season"] == "2024-2025"]
    df_previous_seasons = df_player_game_logs[df_player_game_logs["Season"] != "2024-2025"]

    game_logs_current_html = prepare_player_table(player_name, df_current_season, name_column="Name", no_decimals=True, reverse_order=True)
    game_logs_previous_html = None
    if not df_previous_seasons.empty:
        game_logs_previous_html = prepare_player_table(player_name, df_previous_seasons, name_column="Name", no_decimals=True)

    if not totals_html:
        print(f"⏭️ Skipping {player_name} (no totals data).")
        continue

    html_content = build_html(
        player_name,
        totals_html,
        averages_html or "<p>No data available.</p>",
        per40_html or "<p>No data available.</p>",
        advanced_html or "<p>No data available.</p>",
        game_logs_current_html or "<p>No data available.</p>",
        game_logs_previous_html
    )

    output_file = os.path.join(output_dir, f"{player_name.replace(' ', '_')}_report.pdf")

    HTML(string=html_content, base_url='.').write_pdf(output_file)
    print(f"✅ Generated report for {player_name}: {output_file}")

print("🎉 All player reports generated successfully!")
