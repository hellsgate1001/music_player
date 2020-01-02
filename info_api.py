from pathlib import Path

import requests

base_url = 'https://api.discogs.com/'
token = 'BuvOahnHrVPPEqSLwkTTlSZqyIUTefaMZhFyTuwA'


def check_for_album(releases, album):
    for release in releases:
        if release['title'].lower() == album.lower():
            print('Found release - {}'.format(release['id']))
            return release
    return False


def get_album_info(artist, album, page=1):
    print('Getting album info: {} - {}'.format(artist, album))
    artist_info = get_artist_info(artist)
    while True:
        releases = get_releases_for_artist(artist_info['id'], page)
        album_info = check_for_album(releases['releases'], album)
        if album_info:
            break
        if page < releases['pagination']['pages']:
            page += 1
        else:
            # Album not found at all
            print('Album release not found')
            break
    if album_info:
        # Get the release info
        release_info = get_release_info(album_info['id'])
        if release_info:
            # Store the image
            image_name = '{artist} - {album}.jpg'.format(
                artist=artist.lower(), album=album.lower()
            )
            album_image = Path('static/images/{}'.format(image_name))
            if not album_image.is_file():
                image = get_primary_image(release_info)
                store_image(image_name, image['uri'])


def get_artist_info(artist, page=1):
    print('Getting artist info - {}'.format(artist))
    url = '{base_url}database/search?q={artist}&token={token}&page={page}'.format(
        base_url=base_url, artist=artist, token=token, page=page
    )
    response = requests.get(url)
    res = response.json()
    # Iterate the results looking for type 'artist'
    for result in res['results']:
        if result['type'] == 'artist':
            artist_info = res['results'][0]
            image_name = '{}.jpg'.format(artist_info['title'].lower())
            artist_image = Path('static/images/{}'.format(image_name))
            if not artist_image.is_file():
                store_image(image_name, res['results'][0]['cover_image'])
            return result

    # artist info not found in this page, check the next one
    if page < res['pagination']['pages']:
        return get_artist_info(artist, page + 1)
    return False


def get_primary_image(release_info):
    for image in release_info['images']:
        if image['type'] == 'primary':
            return image
    # return the first image by default
    return release_info['images'][0]


def get_release_info(release_id):
    print('Getting release info {}'.format(release_id))
    url = '{base_url}masters/{release_id}?token={token}'.format(
        base_url=base_url, release_id=release_id, token=token
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print('Error retrieving release {}'.format(release_id))
        return False


def get_releases_for_artist(artist_id, page=1):
    url = '{base_url}artists/{artist_id}/releases?token={token}&page={page}'.format(
        base_url=base_url, artist_id=artist_id, token=token, page=page
    )
    response = requests.get(url)
    return response.json()


def store_image(image_name, img_url):
    img = requests.get(img_url, stream=True)
    if img.status_code == 200:
        with open('static/images/{}'.format(image_name), 'wb') as f:
            for chunk in img:
                f.write(chunk)
    else:
        print('Request error getting image')
