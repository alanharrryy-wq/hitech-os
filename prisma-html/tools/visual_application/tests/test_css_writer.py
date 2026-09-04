import unittest
from visual_application.css_writer import patch_css
from visual_application.errors import TargetNotFound,AmbiguousTarget,PriorityOverrideForbidden,BlockedUnsupportedCss

class CssWriterTests(unittest.TestCase):
    def test_replaces_existing_declaration(self): self.assertIn('color: blue;',patch_css('.a { color: red; }','.a',{'color':'blue'}))
    def test_preserves_other_declaration(self): self.assertIn('padding: 2px;',patch_css('.a { color: red; padding: 2px; }','.a',{'color':'blue'}))
    def test_missing_selector_blocks(self):
        with self.assertRaises(TargetNotFound): patch_css('.a { color:red; }','.b',{'color':'blue'})
    def test_duplicate_selector_blocks(self):
        with self.assertRaises(AmbiguousTarget): patch_css('.a { color:red; } .a { color:blue; }','.a',{'color':'green'})
    def test_missing_property_blocks(self):
        with self.assertRaises(TargetNotFound): patch_css('.a { color:red; }','.a',{'padding':'2px'})
    def test_duplicate_property_blocks(self):
        with self.assertRaises(AmbiguousTarget): patch_css('.a { color:red; color:blue; }','.a',{'color':'green'})
    def test_priority_override_input_blocks(self):
        marker='!'+'important'
        with self.assertRaises(PriorityOverrideForbidden): patch_css(f'.a {{ color:red {marker}; }}','.a',{'color':'blue'})
    def test_priority_override_output_blocks(self):
        marker='!'+'important'
        with self.assertRaises(PriorityOverrideForbidden): patch_css('.a { color:red; }','.a',{'color':'blue '+marker})
    def test_top_level_at_rule_blocks(self):
        with self.assertRaises(BlockedUnsupportedCss): patch_css('@media (min-width:1px){.a{color:red;}}','.a',{'color':'blue'})
    def test_malformed_braces_block(self):
        with self.assertRaises(BlockedUnsupportedCss): patch_css('.a { color:red;','.a',{'color':'blue'})
    def test_comments_and_strings_do_not_break_scanner(self):
        out=patch_css('/* { } */ .a { content:"}"; color:red; }','.a',{'color':'blue'}); self.assertIn('color:blue;',out)
    def test_semicolon_inside_string_is_not_declaration_boundary(self):
        src='.a { content:"x;y:z"; color:red; }'; out=patch_css(src,'.a',{'color':'blue'})
        self.assertIn('content:"x;y:z";',out); self.assertIn('color:blue;',out)
    def test_fake_declaration_in_comment_is_ignored(self):
        src='.a { /* color: purple; */ color:red; }'; out=patch_css(src,'.a',{'color':'blue'})
        self.assertIn('/* color: purple; */',out); self.assertIn('color:blue;',out)
    def test_important_inside_string_is_not_priority(self):
        src='.a { content:"!important"; color:red; }'; out=patch_css(src,'.a',{'color':'blue'})
        self.assertIn('content:"!important";',out)
    def test_unterminated_declaration_blocks(self):
        with self.assertRaises(BlockedUnsupportedCss): patch_css('.a { color:red }','.a',{'color':'blue'})
