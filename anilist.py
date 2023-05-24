import requests
import json

url = 'https://graphql.anilist.co'


def get_multiple(name: str, anime_id: int = None, page: int = 1, status: str = None):
    """Responds with multiple anime which fit the search criteria (name and anime_id). Providing anime_id will always return 1 result.
    If only 1 anime is retrieved, the function will automatically query get_anime() using the id, returning full data. """
    query = """
        query ($search: String, $id: Int, $page: Int, $perpage: Int, $status: MediaStatus) {
            Page (page: $page, perPage: $perpage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                }


                media (search: $search, type: ANIME, id: $id, status: $status) {
                    id
                    title {
                        romaji
                        english
                    }
                }
            }
        }   
    """

    variables = {'perpage': 25}
    if anime_id is not None:
        variables['id'] = anime_id
    if name is not None:
        variables['search'] = name
    if status is not None:
        variables['status'] = status
    variables['page'] = page

    response = json.loads(requests.post(url, json={'query': query, 'variables': variables}).text)
    data = response['data']['Page']

    if data is not None:
        if len(data['media']) == 0:
            return [{'message': 'Not Found', 'status': 404}]
        elif len(data['media']) == 1 and data['pageInfo']['lastPage'] == 1:
            if status == 'RELEASING':
                return get_next_airing_episode(data['media'][0]['id'])
            else:
                return get_anime(data['media'][0]['id'])
        else:
            return data
    else:
        return response['errors']


def get_anime(anime_id: int):
    """Returns all required data formatted, about the anime using the ID. """
    query = """
        query ($id: Int) {
            Media (type: ANIME, id: $id) {
                id
                title {
                    romaji
                    english
                }
                startDate {
                    year
                    month
                    day
                }
                endDate {
                    year
                    month
                    day
                }
                coverImage {
                    large
                    color
                }
                bannerImage
                format
                status
                episodes
                duration
                season
                description
                averageScore
                genres
                nextAiringEpisode {
                    airingAt
                    timeUntilAiring
                    episode
                }
                isAdult
                countryOfOrigin
                siteUrl
                trailer {
                    id
                    site
                }
            }
        }
"""
    variables = {'id': anime_id}

    response = json.loads(requests.post(url, json={'query': query, 'variables': variables}).text)
    data = response['data']['Media']

    if data is not None:

        _id = data['id']

        name_romaji = data['title']['romaji']
        name_english = data['title']['english']

        start_date = f"{data['startDate']['day']}/{data['startDate']['month']}/{data['startDate']['year']}"
        end_date = f"{data['endDate']['day']}/{data['endDate']['month']}/{data['endDate']['year']}"

        cover_image = data['coverImage']['large']
        banner_image = data['bannerImage']
        cover_color = data['coverImage']['color']

        airing_format = data['format']
        airing_status = data['status'].replace('_', ' ').title()
        airing_episodes = data['episodes']
        if airing_status == 'Not Yet Released':
            next_airing_episode = 'Not Yet Release'
        else:
            next_airing_episode = data['nextAiringEpisode']
        season = data['season']
        episode_duration = data['duration']

        description = data['description']
        average_score = data['averageScore']
        genres = data['genres']

        is_adult = data['isAdult']
        origin_country = data['countryOfOrigin'].lower()

        site_url = data['siteUrl']
        if data['trailer'] is None:
            trailer_url = data['trailer']
        else:
            if data['trailer']['site'] == 'youtube':
                trailer_url = f"https://youtube.com/watch?v={data['trailer']['id']}"
            else:
                trailer_url = f"https://dailymotion.com/video/{data['trailer']['id']}"
        formatted_data = {'_id': _id, 'name_romaji': name_romaji, 'name_english': name_english, 'start_date': start_date, 'end_date': end_date, 'cover_image': cover_image,
                          'banner_image': banner_image, 'cover_color': cover_color, 'airing_format': airing_format, 'airing_status': airing_status, 'airing_episodes': airing_episodes,
                          'next_airing_episode': next_airing_episode, 'season': season, 'episode_duration': episode_duration, 'desc': description, 'average_score': average_score,
                          'genres': genres, 'is_adult': is_adult, 'origin_country': origin_country, 'site_url': site_url, 'trailer_url': trailer_url}

        return formatted_data

    else:
        return response['errors']


def get_next_airing_episode(anime_id: int):
    query = """
        query ($id: Int) {
            Media (type: ANIME, id: $id) {
                id
                title {
                    romaji
                    english
                }
                episodes
                nextAiringEpisode {
                    airingAt
                    timeUntilAiring
                    episode
                }
            }
        }
    """

    variables = {'id': anime_id}

    response = json.loads(requests.post(url, json={'query': query, 'variables': variables}).text)
    data = response['data']['Media']

    if data is not None:
        print(data)
        title = data['title']
        next_airing_episode = data['nextAiringEpisode']

        _id = data['id']

        name_english = title['english']
        name_romaji = title['romaji']

        total_episodes = data['episodes']

        if next_airing_episode is None:
            return {'name_english': name_english, 'name_romaji': name_romaji, 'id': _id, 'next_airing_episode': None, 'episodes': total_episodes}

        airing_at = next_airing_episode['airingAt']
        time_until_airing = next_airing_episode['timeUntilAiring']
        episode = next_airing_episode['episode']

        formatted_data = {'name_english': name_english, 'name_romaji': name_romaji, 'airing_at': airing_at, 'time_until_airing': time_until_airing, 'episode': episode, 'id': _id,
                          'next_airing_episode': True, 'episodes': total_episodes}
        return formatted_data
    else:
        return response['errors']


def get_character(char_id: int):
    query = """
    query ($id: Int) {
        Character (id: $id) {
            id
            name {
                full
                alternative
            }
            image {
                large
            }
            description (asHtml: false)
            dateOfBirth {
                year
                month
                day
            }
            gender
            age
            siteUrl
            media (sort: POPULARITY_DESC) {
                edges {
                    node {
                        title {
                            romaji
                            english
                        }
                        type
                    }
                }
            }
        }
    }
    """

    variables = {'id': char_id}

    response = json.loads(requests.post(url=url, json={'query': query, 'variables': variables}).text)
    print(response)

    data = response['data']

    if data is not None:
        data = data['Character']

        _id = data['id']
        name = data['name']['full']
        alt_names = data['name']['alternative']
        description = data['description']
        gender = data['gender']
        age = data['age']
        site_url = data['siteUrl']
        birthdate = f"{data['dateOfBirth']['day']}/{data['dateOfBirth']['month']}/{data['dateOfBirth']['year']}"
        image = data['image']['large']
        appears_in = []
        for media in data['media']['edges']:
            node = media['node']
            appears_in.append({'type': node['type'].lower(), 'name_english': node['title']['english'], 'name_romaji': node['title']['romaji']})

        formatted_data = {'id': _id, 'name': name, 'alt_names': alt_names, 'description': description, 'gender': gender, 'age': age, 'site_url': site_url, 'birthdate': birthdate,
                          'appears_in': appears_in, 'image': image, 'multiple': False}

        return formatted_data
    else:
        return response['errors']


def get_characters(name: str, char_id: int = None, page: int = 1):
    query = """
    query ($name: String, $id: Int, $page: Int, $per_page: Int) {
        Page (page: $page, perPage: $per_page) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
            }

            characters (search: $name, id: $id) {
                id
                name {
                    full
                }
                gender
                media {
                    edges {
                        node {
                            title {
                                english
                                romaji
                            }
                        }
                    }
                }

            }
        }
    }
    """

    variables = {'per_page': 25}
    if name is not None:
        variables['name'] = name
    if char_id is not None:
        variables['id'] = char_id
    variables['page'] = page

    response = json.loads(requests.post(url=url, json={'query': query, 'variables': variables}).text)
    data = response['data']['Page']

    if data is not None:
        if len(data['characters']) == 0:
            return [{'message': 'Not Found', 'status': 404}]
        elif len(data['characters']) == 1:
            return get_character(data['characters'][0]['id'])
        else:
            data['multiple'] = True
            return data
