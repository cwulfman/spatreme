from SPARQLWrapper import SPARQLWrapper2
from pydantic import BaseModel

class QueryResult(BaseModel):
    count: int
    data: list[dict]


class Kb():
    def __init__(self, endpoint: str) -> None:
        self.client: SPARQLWrapper2 = SPARQLWrapper2(endpoint)

    def query(self, querystring) -> QueryResult:
        self.client.setQuery(querystring)
        res = self.client.query()
        results =  [{k : v.value for k,v in result.items()}
                for result in res.bindings]

        return QueryResult(count=len(results), data=results)        


    def languages(self) -> QueryResult:
        q = """PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
select distinct ?lang ?label ?key where { 
	?lang a crm:E56_Language;
       rdfs:label ?label ;
        dcterms:identifier ?key .
}"""
        return self.query(q)
        
    def source_languages(self) -> QueryResult:
        q="""PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
select distinct ?lang ?label ?key where { 
        ?original lrm:R68_is_inspiration_for ?translation .
        ?original lrm:R3i_is_realised_by / crm:P72_has_language ?lang .
        ?lang rdfs:label ?label .
        ?lang dcterms:identifier ?key .
}"""
        return self.query(q)
        
    def target_languages(self) -> QueryResult:
        q="""PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
select distinct ?lang ?label ?key where { 
        ?original lrm:R68_is_inspiration_for ?translation .
        ?translation lrm:R3i_is_realised_by / crm:P72_has_language ?lang .
        ?lang rdfs:label ?label .
        ?lang dcterms:identifier ?key .
}"""
        return self.query(q)
        

    def dates(self) -> QueryResult:
        q="""PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct ?date where { 
?issuetype a crm:E55_Type ;
            dcterms:identifier "issue" .
?issue lrm:P2_has_type ?issuetype .
?issue spatrem:pubDate ?date .
} ORDER BY ?date"""
        return self.query(q)

    def year_births(self) -> QueryResult:
        q="""PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct ?date WHERE {?s spatrem:year_birth ?date .}
order by ?date"""
        return self.query(q)

    def year_deaths(self) -> QueryResult:
        q="""PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct ?date WHERE {?s spatrem:year_death ?date .}
order by ?date"""
        return self.query(q)


    def genres(self) -> QueryResult:
        q="""PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct ?genre where {
	?s spatrem:genre ?genre .    
} order by ?genre"""
        return self.query(q)

    def genders(self) -> QueryResult:
        q="""PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct ?gender where {
    ?person spatrem:gender ?gender .
} order by ?gender"""
        return self.query(q)
 
    def nationalities(self) -> QueryResult:
        q="""PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct ?nationality where {
    ?s spatrem:nationality ?nationality .
} order by ?nationality"""
        return self.query(q)

 
    def language_areas(self) -> QueryResult:
        q="""PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct ?language_area where {
    ?s spatrem:language_area ?language_area .
} order by ?language_area"""
        return self.query(q)


    def magazines(self) -> QueryResult:
        q = """PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct ?magazine ?label ?key
WHERE {
	?type dcterms:identifier "journal" .
	?magazine a lrm:F18_Serial_Work ;
    	          lrm:P2_has_type ?type ;
                  dcterms:identifier ?key ;
		  rdfs:label ?label .
}"""
        return self.query(q)


    def magazine(self, key: str) -> dict:

        q = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct ?magLabel
WHERE {{
        ?magazine dcterms:identifier "{key}" ;
                  rdfs:label ?magLabel .
}}"""
        infodata = self.query(q).data[0]
        info = { "id": key,
                 "title": infodata['magLabel']
                }

        issueq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>        
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct ?issue ?issueLabel ?issueId ?number ?volume ?pubDate
WHERE {{
        ?magazine dcterms:identifier "{key}" ;
                  rdfs:label ?label ;
                  lrm:R67_has_part ?issue .
        ?issue rdfs:label ?issueLabel ;
               dcterms:identifier ?issueId ;
               spatrem:number ?number ;
               spatrem:pubDate ?pubDate .
        OPTIONAL {{ ?issue spatrem:volume ?volume . }}

}} order by ?issueId"""

        issues = []
        for i in self.query(issueq).data:
            issue = {
                "id" : i.get('issueId'),
                "label" : i.get('issueLabel'),
                "volume": i.get('volume'),
                "number": i.get('number'),
                "pubDate" : i.get('pubDate'),
            }
            issues.append(issue)

        return { "info" : info, "issues": issues }

    def issues(self, mag_key: str) -> QueryResult:
        q = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>        
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct *
WHERE {{
        ?magazine dcterms:identifier "{mag_key}" ;
                  rdfs:label ?label ;
                  lrm:R67_has_part ?issue .
        ?issue rdfs:label ?issueLabel ;
               dcterms:identifier ?id ;
               spatrem:number ?no ;
               spatrem:pubDate ?pubDate .
        OPTIONAL {{ ?issue spatrem:volume ?volume . }}

}}"""
        return self.query(q)

    def issue(self, issue_key:str):

        infoq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>        
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct *
WHERE {{
        ?issue dcterms:identifier "{issue_key}" ;
                  lrm:R67i_is_part_of ?magazine ;
                  rdfs:label ?issueLabel ;
                  spatrem:number ?issueNo ;
                  spatrem:pubDate ?pubDate .
        OPTIONAL {{ ?issue spatrem:volume ?volume . }}
        ?magazine rdfs:label ?magLabel ;
                  dcterms:identifier ?magId .
}}"""

        constituentq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>        
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct ?title ?langLabel ?translator ?name ?genre ?author ?authorName ?olangLabel
WHERE {{
        ?issue dcterms:identifier "{issue_key}" .
        ?constituent lrm:R67i_is_part_of ?issue .
        
        ?constituent rdfs:label ?label ;
               lrm:R16i_was_created_by / crm:P14_carried_out_by ?translator ;
               crm:P1_is_identified_by / lrm:R33_has_string ?title ;
               lrm:R3i_is_realised_by / crm:P72_has_language ?tlang ;
               lrm:R68_is_inspired_by ?original ;
               spatrem:genre ?genre .

        ?original lrm:R16i_was_created_by / crm:P14_carried_out_by ?author ;
                  lrm:R3i_is_realised_by / crm:P72_has_language ?olang .
        ?author rdfs:label ?authorName .


        ?tlang rdfs:label ?langLabel .
        ?olang rdfs:label ?olangLabel .
        ?translator rdfs:label ?name .

}}"""
        info = self.query(infoq).data[0]

        constituentdata = self.query(constituentq).data
        constituents = []
        for data in constituentdata:
            c = { "title": data['title'],
                  "language": data['langLabel'],
                  "olanguage": data['olangLabel'],
                  "translator": data['translator'],
                  "name": data['name'],
                  "author": data['author'],
                  "authorName": data['authorName'],
                  "genre": data['genre'] }
            constituents.append(c)
        result = {}
        result['info'] = { "label": info.get("issueLabel"),
                            "magazine": info.get("magazine"),
                            "magLabel": info.get("magLabel"),
                            "magId": info.get("magId"),
                           "volume": info.get("volume"),
                           "number": info.get("issueNo"),
                            "pubDate": info.get("pubDate")}
        result['constituents'] = constituents
        return result

    def constituents(self, issue_key: str) -> QueryResult:
        q = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>        
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct *
WHERE {{
        ?issue dcterms:identifier "{issue_key}" ;
               lrm:R67_has_part ?constituent .
        ?constituent rdfs:label ?issueLabel ;
               lrm:R16i_was_created_by / crm:P14_carried_out_by ?translator ;
               lrm:R3i_is_realised_by / crm:P72_has_language ?tlang .
        ?tlang rdfs:label ?langLabel .
        ?translator rdfs:label ?name .
}}"""
        return self.query(q)

    def constituent(self, con_id: str) -> QueryResult:
        q = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT distinct *
WHERE {{
        spatrem:{con_id} rdfs:label ?label ;
                   lrm:R67i_is_part_of ?issue ;
                   lrm:R68_is_inspired_by ?original ;
                   spatrem:genre ?genre ;
                   lrm:R16i_was_created_by / crm:P14_carried_out_by ?translator ;
                   crm:P1_is_identified_by / lrm:R33_has_string ?title ;
                   lrm:R3i_is_realised_by / crm:P72_has_language ?tlang .
        ?tlang rdfs:label ?langLabel .
        ?original lrm:R16i_was_created_by / crm:P14_carried_out_by ?author ;
                  lrm:R3i_is_realised_by / crm:P72_has_language ?olang .
        ?author rdfs:label ?authorName .
        ?translator rdfs:label ?translatorName .
        ?olang rdfs:label ?olangLabel .
        ?issue rdfs:label ?issue_label ;
           dcterms:identifier ?issue_id ;
           spatrem:pubDate ?pubDate .

}}"""
        return self.query(q)


    def construct_translation_query(self, kwargs: dict) -> str:
        
        q: str = """PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>        
select distinct * where {
	?original lrm:R68_is_inspiration_for ?translation .
    ?original lrm:R16i_was_created_by / crm:P14_carried_out_by ?author .
    ?translation lrm:R16i_was_created_by / crm:P14_carried_out_by ?translator .
    ?original lrm:R3i_is_realised_by / crm:P72_has_language ?olang .
    ?translation lrm:R3i_is_realised_by / crm:P72_has_language ?tlang .
        
    """
        if kwargs['sl'] and kwargs['sl'] != 'any':
            q += f"FILTER(?olang =  <{kwargs['sl']}> )\n"

        if kwargs['tl'] and kwargs['tl'] != 'any':
            q += f"FILTER(?tlang =  <{kwargs['tl']}> )\n"

        q += "?translation spatrem:genre ?genre .\n"

        if kwargs["genre"]  and kwargs['genre'] != 'any':
            q += f"FILTER(?genre =  '{kwargs['genre']}' )\n"


        q += """?issue  spatrem:pubDate ?pubDate ;
                        spatrem:number ?number .
                OPTIONAL { ?issue spatrem:volume ?volume . }
        """


        if kwargs["after_date"] and kwargs['after_date'] != 'any':
            q += f"FILTER(xsd:integer(?pubDate) > {kwargs['after_date']})\n"

        if kwargs["before_date"] and kwargs['before_date'] != 'any':
            q += f"FILTER(xsd:integer(?pubDate) < {kwargs['before_date']})\n"


        q += """?translation lrm:R67i_is_part_of ?issue .
        ?issue lrm:R67i_is_part_of ?magazine .
        """

        if kwargs["magazine"] and kwargs['magazine'] != 'any':
            q += f"FILTER(?magazine = <{kwargs['magazine']}>)\n"


        q += """?translation crm:P1_is_identified_by / lrm:R33_has_string ?title . 
    ?issue rdfs:label ?issue_label ;
           dcterms:identifier ?issue_id .
    ?magazine rdfs:label ?magazine_label ;
           dcterms:identifier ?magazine_id .
    ?author rdfs:label ?author_name .
    ?translator rdfs:label ?translator_name .
    ?olang rdfs:label ?olangLabel .
    ?tlang rdfs:label ?tlangLabel .
    """
        q += "}"

        q += " ORDER BY "

        if "sortby" in kwargs:
            q += f"{ kwargs['sortby'] }"

        q += " ?magazine_id ?pubDate "

        if "offset" in kwargs:
            q += f"OFFSET {kwargs['offset']} "
        
        if "limit" in kwargs:
            q += f"LIMIT {kwargs['limit']} "
        
        return q



    def translations(self, page: int, page_size: int, kwargs: dict = {}) -> QueryResult:
        kwargs["limit"] = page_size
        offset = page - 1
        if offset <= 0:
            offset = 0
        kwargs["offset"] = offset * page_size
        
        query = self.construct_translation_query(kwargs)
        
        return self.query(query)


    def translators(self, kwargs:dict):
        query = """PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>

SELECT distinct *
WHERE {
        ?original lrm:R68_is_inspiration_for ?translation .
        ?translation lrm:R16i_was_created_by / crm:P14_carried_out_by ?translator .
        ?original lrm:R3i_is_realised_by / crm:P72_has_language ?olang .
        ?translation lrm:R3i_is_realised_by / crm:P72_has_language ?tlang .
"""
        if 'sl' in kwargs and kwargs['sl'] != 'any':
            query += f"FILTER(?olang = <{kwargs['sl']}>)\n"

        if 'tl' in kwargs and kwargs['tl'] != 'any':
            query += f"FILTER(?tlang = <{kwargs['tl']}>)\n"

        query += "?translation spatrem:genre ?genre .\n"
        if 'genre' in kwargs and kwargs['genre'] != 'any':
            query += f"FILTER(?genre = '{kwargs['genre']}')\n"


        query += "?translation lrm:R67i_is_part_of / lrm:R67i_is_part_of ?magazine .\n"
        if 'magazine' in kwargs and kwargs['magazine'] != 'any':
            query += f"FILTER(?magazine = <{kwargs['magazine']}>)\n"

        query += """?magazine rdfs:label ?magLabel .
        ?magazine dcterms:identifier ?magKey .
        ?translator rdfs:label ?label .
	?olang rdfs:label ?olangLabel .
        ?tlang rdfs:label ?tlangLabel .
        FILTER(?label != "Anon.")
"""
        if 'gender' in kwargs and kwargs['gender'] != 'any':
            query += f"""?translator spatrem:gender ?gender .
            FILTER(?gender = '{kwargs['gender']}')
            """
        else:
            query += "OPTIONAL { ?translator spatrem:gender ?gender .}\n"


        if 'nationality' in kwargs and kwargs['nationality'] != 'any':
            query += f"""?translator spatrem:nationality ?nationality .
            FILTER(?nationality = '{kwargs['nationality']}')
            """
        else:
            query += "OPTIONAL { ?translator spatrem:nationality ?nationality .}\n"

        if 'language_area' in kwargs and kwargs['language_area'] != 'any':
            query += f"""?translator spatrem:language_area ?language_area .
            FILTER(?language_area = '{kwargs['language_area']}')
            """
        else:
            query += "OPTIONAL { ?translator spatrem:language_area ?language_area .}\n"

        if 'year_birth' in kwargs and kwargs['year_birth'] != 'any':
            query += f"""?translator spatrem:year_birth ?year_birth .
            FILTER(?year_birth > '{kwargs['year_birth']}')
            """
        else:
            query += "OPTIONAL { ?translator spatrem:year_birth ?year_birth .}\n"

        if 'year_death' in kwargs and kwargs['year_death'] != 'any':
            query += f"""?translator spatrem:year_death ?year_death .
            FILTER(?year_death < '{kwargs['year_death']}')
            """
        else:
            query += "OPTIONAL { ?translator spatrem:year_death ?year_death .}\n"



        query += """
} ORDER BY """

        if 'sortby' in kwargs:
            query += f"{kwargs['sortby']} "

        query += "?label"
            
            
        result = self.query(query)

        translators = {}

        for row in result.data:
            id = row['translator']
            if id not in translators:
                translators[row['translator']] = { "id" : id,
                                                   "label" : row.get('label'),
                                                   "gender": row.get('gender'),
                                                   "birthDate": row.get('birthDate'),
                                                   "deathDate": row.get('deathDate'),
                                                   "nationalities": [],
                                                   "language_areas": [],
                                                   "source_langs": [],
                                                   "target_langs": [],
                                                   "genres" : [],
                                                   "magazines": []
                                                  }
                
            if 'nationality' in row and row['nationality'] not in translators[id]['nationalities']:
                translators[id]['nationalities'].append(row['nationality'])

            if 'language_area' in row and row['language_area'] not in translators[id]['language_areas']:
                translators[id]['language_areas'].append(row['language_area'])

            if 'genre' in row and row['genre'] not in translators[id]['genres']:
                translators[id]['genres'].append(row['genre'])

            if 'magLabel' in row and row['magLabel'] not in translators[id]['magazines']:
                translators[id]['magazines'].append(row['magLabel'])

            if 'olangLabel' in row and row['olangLabel'] not in translators[id]['source_langs']:
                translators[id]['source_langs'].append(row['olangLabel'])

            if 'tlangLabel' in row and row['tlangLabel'] not in translators[id]['target_langs']:
                translators[id]['target_langs'].append(row['tlangLabel'])

        # return result
        return translators.values()


    def tlator2(self, uriref):
        workq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX person: <http://spacesoftranslation.org/ns/people/> 
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select distinct ?authorLabel ?olangLabel ?tlangLabel ?magLabel ?genre where {{
    Filter(?persLabel = 'Alegiani, Conte')
    ?translation lrm:R16i_was_created_by / crm:P14_carried_out_by person:{uriref} ;
                     crm:P1_is_identified_by / lrm:R33_has_string ?title ;
                     lrm:R3i_is_realised_by / crm:P72_has_language ?tlang ;
                     lrm:R67i_is_part_of / lrm:R67i_is_part_of ?magazine ;
                     spatrem:genre ?genre .
    
    ?original lrm:R68_is_inspiration_for ?translation ;
    		  lrm:R16i_was_created_by / crm:P14_carried_out_by ?author ;
    			lrm:R3i_is_realised_by / crm:P72_has_language ?olang .
    

        ?tlang rdfs:label ?tlangLabel .
    	?author rdfs:label ?authorLabel .
    	?person rdfs:label ?persLabel .
    	?olang rdfs:label ?olangLabel .
        ?magazine rdfs:label ?magLabel .

       }}"""
        
        results = self.query(workq)
        sl = set()
        tl = set()
        authors = set()
        magazines = set()
        genres = set()

        for row in results.data:
            sl.add(row['olangLabel'])
            tl.add(row['tlangLabel'])
            authors.add(row['authorLabel'])
            magazines.add(row['maglabel'])
            genres.add(row['genre'])
            
    
    def translator(self, uriref):
        infoq = f"""PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
PREFIX person: <http://spacesoftranslation.org/ns/people/> 

SELECT distinct ?label ?birthDate  ?deathDate ?gender ?nationality ?language_area WHERE {{
    person:{uriref} rdfs:label ?label . 	
    OPTIONAL {{ person:{uriref} spatrem:year_birth ?birthDate .}}
    OPTIONAL {{ person:{uriref} spatrem:year_death ?deathDate .}}
    OPTIONAL {{ person:{uriref} spatrem:gender ?gender .}}
    OPTIONAL {{ person:{uriref} spatrem:nationality ?nationality .}}
    OPTIONAL {{ person:{uriref} spatrem:language_area ?language_area .}}
}} ORDER BY ?label"""

        worksq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX person: <http://spacesoftranslation.org/ns/people/> 
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select distinct ?authorLabel ?olangLabel ?tlangLabel ?magLabel ?genre where {{
    Filter(?persLabel = 'Alegiani, Conte')
    ?translation lrm:R16i_was_created_by / crm:P14_carried_out_by person:{uriref} ;
                     crm:P1_is_identified_by / lrm:R33_has_string ?title ;
                     lrm:R3i_is_realised_by / crm:P72_has_language ?tlang ;
                     lrm:R67i_is_part_of / lrm:R67i_is_part_of ?magazine ;
                     spatrem:genre ?genre .
    
    ?original lrm:R68_is_inspiration_for ?translation ;
    		  lrm:R16i_was_created_by / crm:P14_carried_out_by ?author ;
    			lrm:R3i_is_realised_by / crm:P72_has_language ?olang .
    

        ?tlang rdfs:label ?tlangLabel .
    	?author rdfs:label ?authorLabel .
    	?person rdfs:label ?persLabel .
    	?olang rdfs:label ?olangLabel .
        ?magazine rdfs:label ?magLabel .

       }}"""

        namesq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
        PREFIX person: <http://spacesoftranslation.org/ns/people/> 
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
select distinct ?name where {{
        person:{uriref} crm:P1_is_identified_by / lrm:R33_has_string ?name .
        }} """


        info = self.query(infoq).data[0]
        works = self.query(worksq).data
        names = self.query(namesq).data

        sl = set()
        tl = set()
        authors = set()
        magazines = set()
        genres = set()

        for row in works:
            sl.add(row['olangLabel'])
            tl.add(row['tlangLabel'])
            authors.add(row['authorLabel'])
            magazines.add(row['magLabel'])
            genres.add(row['genre'])


        data = {"label": info.get("label"),
                "birthDate" : info.get('birthDate'),
                "deathDate" : info.get('deathDate'),
                "gender" : info.get('gender'),
                "nationality" : info.get('nationality'),
                "language_area" : info.get('language_area'),
                "names": [n['name'] for n in names],
                "source_langs" : [x for x in sl],
                "target_langs" : [x for x in tl],
                "authors" : [x for x in authors],
                "magazines" : [x for x in magazines],
                "genres" : [x for x in genres],
                }

        for field in ['birthDate', 'deathDate', 'gender', 'nationality', 'language_area']:
            if data[field] is None:
                data[field] = 'unknown'

        
        return data

#########

    def translatorOld(self, uriref):
        infoq = f"""PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
PREFIX person: <http://spacesoftranslation.org/ns/people/> 

SELECT distinct ?label ?birthDate  ?deathDate ?gender ?nationality ?language_area WHERE {{
    person:{uriref} rdfs:label ?label . 	
    OPTIONAL {{ person:{uriref} spatrem:year_birth ?birthDate .}}
    OPTIONAL {{ person:{uriref} spatrem:year_death ?deathDate .}}
    OPTIONAL {{ person:{uriref} spatrem:gender ?gender .}}
    OPTIONAL {{ person:{uriref} spatrem:nationality ?nationality .}}
    OPTIONAL {{ person:{uriref} spatrem:language_area ?language_area .}}
}} ORDER BY ?label"""

        infodata = self.query(infoq).data[0]
        info = { "label" : infodata.get('label'),
                 "birthDate" : infodata.get('birthDate'),
                 "deathDate" : infodata.get('deathDate'),
                 "gender" : infodata.get('gender'),
                 "nationality" : infodata.get('nationality'),
                 "language_area" : infodata.get('language_area')
        }
        if info.get('birthDate') is None:
            info['birthDate'] = '?'

        if info.get('deathDate') is None:
            info['deathDate'] = '?'

        if info.get('nationality') is None:
            info['nationality'] = 'unknown'

            
        
        worksq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX person: <http://spacesoftranslation.org/ns/people/> 
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
select distinct * where {{
        ?translation lrm:R16i_was_created_by / crm:P14_carried_out_by person:{uriref} ;
                     crm:P1_is_identified_by / lrm:R33_has_string ?title ;
                     lrm:R3i_is_realised_by / crm:P72_has_language ?tlang ;
                     lrm:R67i_is_part_of ?issue .

        ?tlang rdfs:label ?language .
        ?issue rdfs:label ?issueLabel ;
           dcterms:identifier ?issueId ;
           spatrem:pubDate ?pubDate .

       }} ORDER BY ?pubDate """


        works = []
        for data in self.query(worksq).data:
            work = {
                "title": data['title'],
                "language": data['language'],
                "issue": data["issue"],
                "issueId": data['issueId'],
                "issueLabel": data["issueLabel"],
                "pubDate": data["pubDate"],
                }            
            works.append(work)

        namesq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
        PREFIX person: <http://spacesoftranslation.org/ns/people/> 
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
select distinct ?name where {{
        person:{uriref} crm:P1_is_identified_by / lrm:R33_has_string ?name .
        }} """

        names = [n['name'] for n in self.query(namesq).data]

        return { "works": works, "names": names, "info": info }

########

    def author(self, uriref):
        worksq = f"""PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX person: <http://spacesoftranslation.org/ns/people/> 
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX spatrem: <http://spacesoftranslation.org/ns/spatrem/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select distinct * where {{
        person:{uriref} rdfs:label ?name .
        ?original lrm:R16i_was_created_by / crm:P14_carried_out_by person:{uriref} ;
                  lrm:R3i_is_realised_by / crm:P72_has_language ?olang .
    
        ?translation lrm:R68_is_inspired_by ?original ;
                     lrm:R16i_was_created_by / crm:P14_carried_out_by ?translator ;
                     rdfs:label ?title ;
                     lrm:R3i_is_realised_by / crm:P72_has_language ?tlang ;
                     lrm:R67i_is_part_of ?issue .

        ?tlang rdfs:label ?tlanguage .
    	?translator rdfs:label ?tname .
        ?olang rdfs:label ?olanguage .
        ?issue rdfs:label ?issueLabel ;
           dcterms:identifier ?issueId ;
           spatrem:pubDate ?pubDate .

        }}"""
        return self.query(worksq)
