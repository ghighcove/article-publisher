"""
Table Image Generator
Creates professional-looking table images from data using PIL/Pillow
"""

from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Optional, Tuple
import os


class TableImageGenerator:
    """Generates table images with professional styling"""

    def __init__(self, style_config: Optional[Dict] = None):
        """
        Initialize the table image generator

        Args:
            style_config: Optional dictionary with styling preferences
        """
        self.style = self._get_default_style()
        if style_config:
            self.style.update(style_config)

    def _get_default_style(self) -> Dict:
        """Get default styling configuration"""
        return {
            'bg_color': (255, 255, 255),  # White background
            'header_bg': (41, 128, 185),  # Professional blue
            'header_text': (255, 255, 255),  # White text
            'row_bg_1': (236, 240, 241),  # Light gray (alternating)
            'row_bg_2': (255, 255, 255),  # White (alternating)
            'text_color': (44, 62, 80),  # Dark gray text
            'border_color': (189, 195, 199),  # Light border
            'font_size_header': 18,
            'font_size_data': 16,
            'padding': 15,
            'cell_padding': 10,
            'border_width': 1,
            'min_col_width': 120,
        }

    def _get_font(self, size: int, bold: bool = False):
        """Get font with fallback options"""
        font_options = [
            'arial.ttf',
            'Arial.ttf',
            'helvetica.ttf',
            'DejaVuSans.ttf',
            'LiberationSans-Regular.ttf',
        ]

        if bold:
            bold_options = [
                'arialbd.ttf',
                'Arial-Bold.ttf',
                'helvetica-bold.ttf',
                'DejaVuSans-Bold.ttf',
                'LiberationSans-Bold.ttf',
            ]
            font_options = bold_options + font_options

        for font_name in font_options:
            try:
                return ImageFont.truetype(font_name, size)
            except:
                continue

        # Fallback to default font
        return ImageFont.load_default()

    def _calculate_column_widths(self, headers: List[str], rows: List[List[str]],
                                  draw, header_font, data_font) -> List[int]:
        """Calculate optimal column widths based on content"""
        num_cols = len(headers)
        col_widths = [self.style['min_col_width']] * num_cols

        # Check header widths
        for i, header in enumerate(headers):
            bbox = draw.textbbox((0, 0), header, font=header_font)
            width = bbox[2] - bbox[0] + (2 * self.style['cell_padding'])
            col_widths[i] = max(col_widths[i], width)

        # Check data widths
        for row in rows:
            for i, cell in enumerate(row):
                bbox = draw.textbbox((0, 0), str(cell), font=data_font)
                width = bbox[2] - bbox[0] + (2 * self.style['cell_padding'])
                col_widths[i] = max(col_widths[i], width)

        return col_widths

    def _calculate_row_height(self, text: str, font, max_width: int, draw) -> int:
        """Calculate row height based on text and potential wrapping"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_height = bbox[3] - bbox[1]
        return text_height + (2 * self.style['cell_padding'])

    def create_table_image(self, headers: List[str], rows: List[List[str]],
                           output_path: str, title: Optional[str] = None) -> str:
        """
        Create a table image from data

        Args:
            headers: List of column headers
            rows: List of row data (each row is a list of cell values)
            output_path: Path to save the image
            title: Optional title to display above table

        Returns:
            Path to the created image
        """
        # Create temporary image to measure text
        temp_img = Image.new('RGB', (100, 100), self.style['bg_color'])
        temp_draw = ImageDraw.Draw(temp_img)

        # Get fonts
        header_font = self._get_font(self.style['font_size_header'], bold=True)
        data_font = self._get_font(self.style['font_size_data'])
        title_font = self._get_font(24, bold=True) if title else None

        # Calculate column widths
        col_widths = self._calculate_column_widths(headers, rows, temp_draw,
                                                     header_font, data_font)

        # Calculate dimensions
        table_width = sum(col_widths) + (len(col_widths) + 1) * self.style['border_width']
        row_height = 50  # Fixed row height for simplicity
        header_height = row_height

        title_height = 0
        if title:
            title_bbox = temp_draw.textbbox((0, 0), title, font=title_font)
            title_height = title_bbox[3] - title_bbox[1] + 40  # Extra padding

        total_height = (title_height +
                       header_height +
                       (len(rows) * row_height) +
                       (len(rows) + 2) * self.style['border_width'] +
                       2 * self.style['padding'])

        img_width = table_width + 2 * self.style['padding']
        img_height = total_height

        # Create the actual image
        img = Image.new('RGB', (img_width, img_height), self.style['bg_color'])
        draw = ImageDraw.Draw(img)

        current_y = self.style['padding']

        # Draw title if present
        if title:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (img_width - title_width) // 2
            draw.text((title_x, current_y), title, fill=self.style['text_color'],
                     font=title_font)
            current_y += title_height

        # Draw header row
        current_x = self.style['padding']
        for i, header in enumerate(headers):
            # Draw header background
            draw.rectangle([current_x, current_y,
                          current_x + col_widths[i],
                          current_y + header_height],
                         fill=self.style['header_bg'],
                         outline=self.style['border_color'],
                         width=self.style['border_width'])

            # Draw header text (centered)
            text_bbox = draw.textbbox((0, 0), header, font=header_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = current_x + (col_widths[i] - text_width) // 2
            text_y = current_y + (header_height - text_height) // 2

            draw.text((text_x, text_y), header, fill=self.style['header_text'],
                     font=header_font)

            current_x += col_widths[i]

        current_y += header_height

        # Draw data rows
        for row_idx, row in enumerate(rows):
            current_x = self.style['padding']
            bg_color = self.style['row_bg_1'] if row_idx % 2 == 0 else self.style['row_bg_2']

            for col_idx, cell in enumerate(row):
                # Draw cell background
                draw.rectangle([current_x, current_y,
                              current_x + col_widths[col_idx],
                              current_y + row_height],
                             fill=bg_color,
                             outline=self.style['border_color'],
                             width=self.style['border_width'])

                # Draw cell text (left-aligned with padding)
                text_bbox = draw.textbbox((0, 0), str(cell), font=data_font)
                text_height = text_bbox[3] - text_bbox[1]
                text_x = current_x + self.style['cell_padding']
                text_y = current_y + (row_height - text_height) // 2

                draw.text((text_x, text_y), str(cell), fill=self.style['text_color'],
                         font=data_font)

                current_x += col_widths[col_idx]

            current_y += row_height

        # Save the image
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        img.save(output_path, 'PNG', quality=95)

        return output_path


# Example usage
if __name__ == '__main__':
    generator = TableImageGenerator()

    # Test with a simple table
    headers = ['Name', 'Position', 'Value']
    rows = [
        ['Player 1', 'QB', '+0.50'],
        ['Player 2', 'RB', '+0.25'],
        ['Player 3', 'WR', '+0.75'],
    ]

    generator.create_table_image(headers, rows, 'test_table.png', title='Test Table')
    print('Test table created: test_table.png')
