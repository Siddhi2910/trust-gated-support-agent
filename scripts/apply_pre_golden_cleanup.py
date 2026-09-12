import json
import pandas as pd

def main():
    df = pd.read_parquet('data/processed/applesupport_conversations.parquet')
    inbound = df[df['root_inbound'] == True].copy()
    lookup = dict(zip(inbound['root_tweet_id'], inbound['customer_inquiry_text']))
    conv_lookup = dict(zip(inbound['root_tweet_id'], inbound['conversation_id']))

    with open('artifacts/taxonomy_human_review_sample.json', 'r', encoding='utf-8') as f:
        sample_data = json.load(f)

    # Part 2 replacements
    p2_replaces = {
        3: 254686,    # Case 124
        4: 146710,    # Case 125
        8: 1000235,   # Case 129
        11: 324534,   # Case 132
        13: 804109,   # Case 134
        16: 2082705,  # Case 137
        17: 2732870,  # Case 138
        18: 1948006,  # Case 139
        22: 234621,   # Case 143
        27: 619390,   # Case 148
        29: 846969,   # Case 150
        30: 1153873   # Case 151
    }

    for idx, new_tid in p2_replaces.items():
        item = sample_data['part_2_boundary_cases'][idx]
        item['tweet_id'] = new_tid
        item['conversation_id'] = conv_lookup[new_tid]
        item['text'] = lookup[new_tid]

    # Part 3 replacements
    p3_replaces = {
        0: (1392452, 'CATEGORY_A_NON_SUPPORT', 'Commercial product pre-order announcement broadcast; contains no customer support inquiry.'),
        1: (2726010, 'CATEGORY_A_NON_SUPPORT', 'Launch celebration coworker tweet / non-support social commentary.'),
        5: (52273, 'CATEGORY_B1_BARE_PLEA_PING', 'Bare conversational plea directed to AppleSupport with zero diagnostic symptom or component named.'),
        6: (167286, 'CATEGORY_B1_BARE_PLEA_PING', 'Bare conversational DM request directed to AppleSupport with zero diagnostic symptom or component named.'),
        7: (408455, 'CATEGORY_B1_BARE_PLEA_PING', 'Bare conversational cry for help and DM request with zero diagnostic symptom named.'),
        11: (162838, 'CATEGORY_B2_MEDIA_LINK_ONLY', 'Media/URL attachment with conversational remark "Lol look" and zero textual symptom; text alone provides insufficient context.'),
        12: (1302379, 'CATEGORY_B3_SYMPTOMLESS_RANT', 'Pure emotional frustration rant against update with zero diagnostic symptom or component identified.')
    }

    for idx, (new_tid, cat, reason) in p3_replaces.items():
        item = sample_data['part_3_unknown_cases'][idx]
        item['tweet_id'] = new_tid
        item['conversation_id'] = conv_lookup[new_tid]
        item['text'] = lookup[new_tid]
        item['category'] = cat
        item['reason_not_technical'] = reason

    # Save sample JSON
    with open('artifacts/taxonomy_human_review_sample.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    print('Updated artifacts/taxonomy_human_review_sample.json successfully.')

if __name__ == '__main__':
    main()
