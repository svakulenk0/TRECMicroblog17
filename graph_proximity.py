# -*- coding: utf-8 -*-
'''
svakulenko
24 july 2017
'''

from conceptualization import get_concepts_from_lotus, lookup


TOPIC = {
           "narrative" : "@SwiftOnSecurity is a great twitter account about IT security that targets a broad audience. Tweets from the similar accounts on the IT security topic are also relevant.",
           "title" : "IT security",
           "topid" : "RTS219",
           "description" : "News and reflections about IT security."
        }

TRUE = [
        "Just to spell this out: The logging capabilities in PowerShell are so incredibly empowering to defenders that attackers getting worried.",
        "If you're configuring your corporate antivirus to send no threat data and only get updates from your AV server, you're far more vulnerable.",
        '''Approximately 96% of all [malware hashes] detected and blocked by Windows Defender Antivirus (Windows Defender AV) are observed only once'''
        ]
FALSE = [
         "What about references and security clearance lol",
         "Security Cams - Best Source for Security Cameras, Surveillance Systems and Security DVRs http://ref.gl/kbxCwBQj ",
         "ಇಂಡಿಯನ್ politicians n border security force also have their good share...",
         '''••Great Full Time Benefits at General Security Services Corporation!•• http://JobGuideND.com''',
        ]


def main():
    title = TOPIC['title']
    concept, text = get_concepts_from_lotus(title)
    concept_uri = list(concept)[0]
    print concept_uri
    print lookup(concept_uri)


if __name__ == '__main__':
    main()
