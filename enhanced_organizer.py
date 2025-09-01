import os
import json
import random
import shutil
from pathlib import Path
from typing import List, Dict


class ImprovedYoloDatasetOrganizer:
    def __init__(self, input_dir: str, output_dir: str, class_mapping: Dict[str, int]=None):
        # UI class mapping (from improved_organizer.py)
        self.class_mapping = {
            'android.widget.Button': 'button',
            'android.widget.ImageButton': 'button',
            'android.support.v7.widget.AppCompatButton': 'button',
            'android.support.v7.widget.AppCompatImageButton': 'button',
            'android.support.design.widget.FloatingActionButton': 'button',
            'com.google.android.gms.plus.PlusOneButton': 'button',
            'com.kakao.usermgmt.LoginButton': 'button',
            'com.path.base.views.widget.PartlyRoundedButton': 'button',
            'android.widget.ActionMenuPresenter$OverflowMenuButton': 'button',
            'android.widget.TextView': 'text',
            'android.support.v7.widget.AppCompatTextView': 'text',
            'com.global.foodpanda.android.custom.views.FoodPandaTextView': 'text',
            'com.twoergo.foxbusinessnews.widget.FBNTextView': 'text',
            'com.google.android.finsky.layout.LinkTextView': 'text',
            'com.bbva.compassBuzz.commons.ui.widget.CustomTextView': 'text',
            'android.widget.EditText': 'input',
            'android.support.v7.widget.AppCompatEditText': 'input',
            'android.widget.AutoCompleteTextView': 'input',
            'android.widget.MultiAutoCompleteTextView': 'input',
            'android.widget.ImageView': 'image',
            'android.support.v7.widget.AppCompatImageView': 'image',
            'android.widget.FrameLayout': 'container',
            'android.widget.LinearLayout': 'container',
            'android.widget.RelativeLayout': 'container',
            'android.widget.ScrollView': 'container',
            'android.widget.HorizontalScrollView': 'container',
            'android.widget.GridView': 'container',
            'android.widget.GridLayout': 'container',
            'android.widget.TableLayout': 'container',
            'android.widget.TableRow': 'container',
            'android.widget.TabHost': 'navigation',
            'android.support.design.widget.BottomNavigationView': 'navigation',
            'android.support.design.widget.NavigationView': 'navigation',
            'android.support.v7.widget.Toolbar': 'toolbar',
            'android.widget.ActionMenuView': 'toolbar',
            'android.widget.CheckBox': 'checkbox',
            'android.widget.RadioButton': 'radio',
            'android.widget.RadioGroup': 'radio',
            'android.widget.SeekBar': 'slider',
            'android.widget.ProgressBar': 'progress',
            'android.widget.Switch': 'checkbox',
            'android.widget.ToggleButton': 'checkbox',
            'android.support.v7.widget.CardView': 'card',
            'android.widget.ListView': 'list_item',
            'android.widget.RecyclerView': 'list_item',
            'android.support.v7.widget.RecyclerView': 'list_item',
            'android.widget.ExpandableListView': 'list_item',
            'android.webkit.WebView': 'webview',
            'org.apache.cordova.engine.SystemWebView': 'webview',
            'com.google.android.gms.ads.AdView': 'ad',
            'com.facebook.ads.AdView': 'ad',
        }
        self.ui_classes = {
            'button': 0,
            'text': 1,
            'input': 2,
            'image': 3,
            'container': 4,
            'navigation': 5,
            'checkbox': 6,
            'radio': 7,
            'slider': 8,
            'progress': 9,
            'toolbar': 10,
            'card': 11,
            'list_item': 12,
            'webview': 13,
            'ad': 14
        }
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.stats = {
            "total_images": 0,
            "used_images": 0,
            "skipped_images": 0,
            "total_elements": 0,
            "used_elements": 0,
        }

    def is_meaningful_element(self, node: Dict, bounds: List[int], img_width: int, img_height: int) -> bool:
        # Bounds must be a list of 4 numbers
        if not (isinstance(bounds, list) and len(bounds) == 4 and all(isinstance(x, (int, float)) for x in bounds)):
            print(f"[SKIP] Invalid bounds: {bounds} for node: {node.get('class', 'unknown')}")
            return False

        x_min, y_min, x_max, y_max = bounds
        if x_max <= x_min or y_max <= y_min:
            print(f"[SKIP] Non-positive width/height: {bounds} for node: {node.get('class', 'unknown')}")
            return False

        area = (x_max - x_min) * (y_max - y_min)
        total_area = img_width * img_height
        area_ratio = area / total_area

        # Lowered minimum area threshold for inclusivity
        if area_ratio < 0.0001:
            print(f"[SKIP] Too small area: {area_ratio:.6f} for node: {node.get('class', 'unknown')}")
            return False
        if area_ratio > 0.95:
            print(f"[SKIP] Too large area: {area_ratio:.6f} for node: {node.get('class', 'unknown')}")
            return False

        # Accept if any of these are true
        if node.get('clickable', False):
            return True
        if node.get('focusable', False):
            return True
        if node.get('text', '') and node.get('text', '').strip():
            return True
        if node.get('content-desc') and str(node.get('content-desc')).strip():
            return True
        if node.get('visible-to-user', True):
            return True

        print(f"[SKIP] Not interactive/visible/text: {node.get('class', 'unknown')}")
        return False

    def classify_element(self, node: Dict) -> str:
        if 'class' not in node:
            return None
        android_class = node['class']
        if android_class in self.class_mapping:
            return self.class_mapping[android_class]
        # Fallback logic
        is_clickable = node.get('clickable', False)
        has_text = bool(node.get('text', '').strip())
        has_content_desc = bool(node.get('content-desc', [None])[0])
        if is_clickable and (has_text or has_content_desc):
            return 'button'
        elif has_text or has_content_desc:
            return 'text'
        elif is_clickable:
            return 'button'
        elif android_class.endswith('View') and not android_class.endswith('ImageView'):
            return 'container'
        return None

    def convert_bounds_to_yolo(self, bounds: List[int], img_width: int, img_height: int):
        x_min, y_min, x_max, y_max = bounds
        x_center = (x_min + x_max) / 2.0 / img_width
        y_center = (y_min + y_max) / 2.0 / img_height
        width = (x_max - x_min) / img_width
        height = (y_max - y_min) / img_height
        return x_center, y_center, width, height

    def create_yolo_annotation(self, elements: List[Dict], img_width: int, img_height: int):
        yolo_lines = []
        for el in elements:
            class_name = el.get('class')
            bounds = el.get('bounds')
            if class_name not in self.ui_classes:
                continue
            if not bounds or len(bounds) != 4:
                continue
            x, y, w, h = self.convert_bounds_to_yolo(bounds, img_width, img_height)
            if w <= 0 or h <= 0 or w > 1 or h > 1:
                continue
            class_id = self.ui_classes[class_name]
            yolo_lines.append(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
        return yolo_lines

    def process_dataset(self):
        all_images = list(self.input_dir.glob("*.jpg"))
        random.shuffle(all_images)

        split = [0.8, 0.1, 0.1]
        n = len(all_images)
        train, val, test = (
            all_images[:int(n * split[0])],
            all_images[int(n * split[0]):int(n * (split[0] + split[1]))],
            all_images[int(n * (split[0] + split[1])):]
        )
        splits = {'train': train, 'val': val, 'test': test}

        for phase in ['train', 'val', 'test']:
            img_out = self.output_dir / 'images' / phase
            lbl_out = self.output_dir / 'labels' / phase
            img_out.mkdir(parents=True, exist_ok=True)
            lbl_out.mkdir(parents=True, exist_ok=True)

        class_counter = {}
        for phase, image_list in splits.items():
            for img_path in image_list:
                json_path = self.input_dir / (img_path.stem + '.json')
                if not json_path.exists():
                    self.stats['skipped_images'] += 1
                    continue

                try:
                    with open(json_path, 'r') as f:
                        ui_data = json.load(f)
                except Exception as e:
                    print(f"Error reading JSON {json_path}: {e}")
                    self.stats.setdefault('invalid_json', 0)
                    self.stats['invalid_json'] += 1
                    continue

                img_width, img_height = 1080, 1920  # Modify if dynamic
                elements = []
                nodes = ui_data.get('activity', {}).get('root', {}).get('children', [])

                def collect_nodes(n):
                    if not isinstance(n, dict):
                        return
                    if 'children' in n and n['children']:
                        for child in n['children']:
                            collect_nodes(child)
                    if 'bounds' in n:
                        bounds = n['bounds']
                        ui_class = self.classify_element(n)
                        if ui_class and ui_class in self.ui_classes and self.is_meaningful_element(n, bounds, img_width, img_height):
                            class_name = ui_class
                            class_counter[class_name] = class_counter.get(class_name, 0) + 1
                            n['class'] = class_name
                            n['bounds'] = bounds
                            elements.append(n)
                        else:
                            class_name = ui_class if ui_class else n.get('class', 'unknown')
                            class_counter[class_name] = class_counter.get(class_name, 0)

                for node in nodes:
                    collect_nodes(node)

                yolo_lines = self.create_yolo_annotation(elements, img_width, img_height)
                if not yolo_lines:
                    self.stats['skipped_images'] += 1
                    continue

                # Copy image
                img_out = self.output_dir / 'images' / phase / img_path.name
                shutil.copy(img_path, img_out)

                # Write label
                label_path = self.output_dir / 'labels' / phase / (img_path.stem + '.txt')
                with open(label_path, 'w') as f:
                    f.write('\n'.join(yolo_lines))

                self.stats['used_images'] += 1
                self.stats['used_elements'] += len(yolo_lines)

        print("\n✅ Dataset processing complete.")
        print(f"Total images found: {len(all_images)}")
        print(f"Images used: {self.stats['used_images']}")
        print(f"Images skipped (no/empty labels or missing JSON): {self.stats['skipped_images']}")
        print(f"Images with invalid/malformed JSON: {self.stats.get('invalid_json', 0)}")
        print(f"Total elements labeled: {self.stats['used_elements']}")
        print("\nINSIGHTS:")
        total = len(all_images)
        skipped = self.stats['skipped_images']
        invalid = self.stats.get('invalid_json', 0)
        used = self.stats['used_images']
        print(f"- {skipped+invalid} out of {total} images (\u2248 {100*(skipped+invalid)/total:.2f}%) were not usable (skipped or invalid)")
        print(f"- {used} out of {total} images (\u2248 {100*used/total:.2f}%) were successfully converted to YOLO format")
        print(f"- If the unusable rate is high, dataset may contain many incomplete or malformed UI trees. Consider further cleaning or error analysis.")

        print("\nClass distribution (including skipped):")
        for cls, count in class_counter.items():
            print(f"- {cls}: {count}")


if __name__ == "__main__":
    class_mapping = {
        "TextView": 0,
        "ImageView": 1,
        "Button": 2,
        "EditText": 3,
        "CheckBox": 4,
        "RadioButton": 5,
        "Switch": 6,
        "SeekBar": 7,
        "WebView": 8,
        "View": 9
    }

    organizer = ImprovedYoloDatasetOrganizer(
        input_dir="combined",
        output_dir="improved_dataset",
        class_mapping=class_mapping
    )

    organizer.process_dataset()
