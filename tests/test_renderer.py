# tests/test_renderer.py
from listinggen.engine.renderer import render_prompt
from listinggen.engine.types import ListingInput, GenTask      

def test_render_prompt_basic():
    listing = ListingInput(sku="A001", source_title="Test Title", keywords="k1,k2")
    task = GenTask(name="title")

    system_prompt, user_prompt = render_prompt(listing, task)

    assert isinstance(system_prompt, str) and system_prompt
    assert isinstance(user_prompt, str) and user_prompt
    assert "A001" in user_prompt
