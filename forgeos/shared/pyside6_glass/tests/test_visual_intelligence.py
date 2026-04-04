from pyside6_glass.appearance import VisualIntelligenceContext, select_visual_bundle


def test_visual_intelligence_is_deterministic_for_same_context():
    context = VisualIntelligenceContext(
        experience_mode='monitoring',
        requested_visual_level='premium',
        data_state='stale',
        reduced_motion=False,
        high_contrast_mode=False,
        data_density_bias=0.4,
    )
    first = select_visual_bundle(context)
    second = select_visual_bundle(context)
    assert first.profile.to_dict() == second.profile.to_dict()
    assert first.effects.to_dict() == second.effects.to_dict()
    assert first.effective_level == second.effective_level
    assert first.preset_name == second.preset_name


def test_visual_intelligence_respects_reduced_motion_and_downgrades_showcase():
    context = VisualIntelligenceContext(
        experience_mode='presentation',
        requested_visual_level='showcase',
        data_state='ready',
        reduced_motion=True,
    )
    bundle = select_visual_bundle(context)
    assert bundle.profile.reduced_motion is True
    assert bundle.profile.animation_level in {'off', 'subtle'}
    assert bundle.effects.motion_enabled is False
    assert bundle.effective_level != 'showcase'

