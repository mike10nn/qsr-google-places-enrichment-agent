from qsr_google_enricher.classifier import classify_location_type


def test_transport_hub_keyword():
    label, confidence, manual, _ = classify_location_type(
        formatted_address="Stazione Centrale, Milano, Italy",
        display_name="McDonald's",
        place_types=["restaurant"],
        nearby_context=[],
    )
    assert label == "Transport Hub"
    assert confidence > 0.8
    assert manual is False


def test_shopping_mall_keyword():
    label, confidence, manual, _ = classify_location_type(
        formatted_address="Centro Commerciale Globo, Busnago, Italy",
        display_name="Burger King",
        place_types=["restaurant"],
        nearby_context=[],
    )
    assert label == "Shopping Mall"
    assert confidence > 0.9
    assert manual is False
