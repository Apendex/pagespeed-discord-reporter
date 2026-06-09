import json
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

def get_color_scheme(score):
    """Returns the main color and background tint based on the score."""
    if score is None:
        return '#CBD5E1', '#F8FAFC'  # Gray fallback
    if score >= 90:
        return '#00CC66', '#E6F9F0'  # Green
    elif score >= 50:
        return '#FFA400', '#FFF6E6'  # Orange
    else:
        return '#FF4E42', '#FFEDEB'  # Red

def draw_dial(ax, score, title):
    """Draws a single donut chart dial on a given matplotlib axis."""
    if score is None:
        ax.axis('off')
        return

    main_color, bg_color = get_color_scheme(score)
    
    # Pie chart data
    sizes = [score, 100 - score]
    colors = [main_color, bg_color]
    
    ax.pie(sizes, colors=colors, startangle=90, counterclock=False, 
           wedgeprops=dict(width=0.18, edgecolor='none'))
    
    # Score in the center
    ax.text(0, 0, str(score), ha='center', va='center', 
            fontsize=32, fontweight='bold', color=main_color)
    
    # Category label beneath
    ax.text(0, -1.4, title, ha='center', va='center', 
            fontsize=14, color='#4B5563', fontweight='medium')
    
    ax.axis('equal') 

def create_dashboard_image(json_filename="pagespeed_insights_results.json", output_filename="pagespeed_insights_results.png"):
    """Reads JSON data and generates a styled dashboard image."""
    
    if not os.path.exists(json_filename):
        print(f"Error: '{json_filename}' not found.")
        return

    with open(json_filename, 'r') as f:
        data = json.load(f)

    categories = ["performance", "accessibility", "best-practices", "seo"]
    strategies = ["mobile", "desktop"]
    available_strategies = [s for s in strategies if s in data]
    
    if not available_strategies:
        print("No valid strategy data found in the JSON file.")
        return

    # --- 1. Figure Setup ---
    # Dark background to match Discord
    fig = plt.figure(figsize=(12, 8), facecolor='#2B2D31')

    # --- 2. Draw the White Card ---
    # Coordinates: [left, bottom, width, height]
    card_ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    card_ax.axis('off')
    card = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03",
                          ec="none", fc="white", transform=card_ax.transAxes)
    card_ax.add_patch(card)

    # --- 3. Header Text ---
    url = data.get("url", "Website Performance Report")
    timestamp = data.get("timestamp", "Time not specified")
    
    fig.text(0.1, 0.87, f"PageSpeed Insights for {url}", fontsize=20, fontweight='bold', color='#111827', ha='left')
    fig.text(0.1, 0.83, f"Report Generated: {timestamp}", fontsize=14, color='#6B7280', ha='left')
    
    # Header Divider Line
    fig.add_artist(plt.Line2D((0.1, 0.9), (0.80, 0.80), color='#F3F4F6', linewidth=2))

    # --- 4. Render the Dials ---
    # Using GridSpec to perfectly align the dials inside the card
    gs = fig.add_gridspec(nrows=len(available_strategies), ncols=4, 
                          left=0.25, right=0.9, top=0.72, bottom=0.22, hspace=0.4)

    for row_idx, strategy in enumerate(available_strategies):
        # Extract scores from the full API response structure
        strategy_full_data = data[strategy]
        lighthouse_result = strategy_full_data.get('lighthouseResult', {})
        strategy_categories = lighthouse_result.get('categories', {})
        
        # Add the row label (Mobile/Desktop) relative to the first dial in the row
        ax_first = fig.add_subplot(gs[row_idx, 0])
        ax_first.annotate(f"{strategy.capitalize()}", xy=(-0.4, 0.5), xycoords='axes fraction',
                          fontsize=16, fontweight='bold', ha='right', va='center', color='#1F2937')

        for col_idx, category in enumerate(categories):
            # Only create a new subplot if it's not the first one (which we already created for the label)
            ax = ax_first if col_idx == 0 else fig.add_subplot(gs[row_idx, col_idx])
            
            category_data = strategy_categories.get(category, {})
            score_val = category_data.get('score')
            score = int(score_val * 100) if score_val is not None else None
            
            display_title = "SEO" if category == "seo" else category.replace('-', ' ').title()
            
            draw_dial(ax, score, display_title)

    # --- 5. Footer Insights Bar ---
    # Dynamically generate a tip based on the lowest critical score
    mobile_full_data = data.get("mobile", {})
    mobile_lighthouse = mobile_full_data.get('lighthouseResult', {})
    mobile_categories = mobile_lighthouse.get('categories', {})
    mobile_perf_data = mobile_categories.get('performance', {}).get('score', 1.0)
    mobile_perf = int(mobile_perf_data * 100)
    
    if mobile_perf < 50:
        insight_msg = "Insight: Mobile Performance is in the red. Prioritize optimizing images and reducing main-thread work."
        msg_color = '#B91C1C' # Dark Red
        bg_color = '#FEF2F2'  # Light Red
    elif mobile_perf < 90:
        insight_msg = "Insight: Mobile Performance needs improvement. Look into unused CSS/JS and cache policies."
        msg_color = '#B45309' # Dark Orange
        bg_color = '#FFFBEB'  # Light Orange
    else:
        insight_msg = "Insight: Fantastic! All primary metrics are looking highly optimized."
        msg_color = '#047857' # Dark Green
        bg_color = '#ECFDF5'  # Light Green

    # Draw footer box
    footer_ax = fig.add_axes([0.1, 0.08, 0.8, 0.06])
    footer_ax.axis('off')
    footer_bg = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.3",
                               ec="none", fc=bg_color, transform=footer_ax.transAxes)
    footer_ax.add_patch(footer_bg)
    footer_ax.text(0.02, 0.5, insight_msg, fontsize=11, fontweight='bold', color=msg_color, va='center', ha='left')

    # --- 6. Save ---
    # facecolor=fig.get_facecolor() ensures the Discord-dark margins are preserved
    # bbox_inches='tight' and pad_inches=0 remove any extra gray padding
    plt.savefig(output_filename, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0)
    print(f"Successfully generated {output_filename}")

if __name__ == "__main__":
    create_dashboard_image()