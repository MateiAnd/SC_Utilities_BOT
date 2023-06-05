import json


def get_org_by_msg_id(msg_id: int):
    with open('./organizari_bot/organizari.json', 'r') as f:
        _temp = json.load(f)
    org_data = _temp['org']
    for org in org_data:
        if org["Message_id"] == msg_id:
            return org
    else:
        return {}


def make_reminder_string(org_dict, letter: str, time: str):
    participants = org_dict['Participants']

    template_string = '''{letter} mai ramas __**{timp}**__ pana la organizarea a lui <@{sherpa}>.
Participanti: {participanti}
Rezerve: {queue} {rezerve}'''

    participanti = ' '.join(['<@{}>'.format(exp[1]) for exp in participants['Participants']])
    queue = ' '.join(['<@{}>'.format(que[1]) for que in participants['Queue']])
    rezerve = ' '.join(['<@{}>'.format(rez[1]) for rez in participants['Reserve']])

    out_str = template_string.format(letter=letter, timp=time, sherpa=participants['Author'][1],
                                     participanti=participanti, queue=queue, rezerve=rezerve)
    return out_str


def data_updater(org_old, org_new):
    with open('./organizari_bot/organizari.json', 'r') as f:
        _temp = json.load(f)

    _temp = _temp['org']
    for _org in _temp:
        if _org == org_old:
            _temp.remove(_org)
            if org_new:
                _temp.append(org_new)

    new_dump = {'org': _temp}

    with open('./organizari_bot/organizari.json', 'w') as f:
        json.dump(new_dump, f)
