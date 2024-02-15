import json


def test_create_summary(test_app_with_db):
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo.bar'}))
    assert response.status_code == 201
    assert response.json()['url'] == 'https://foo.bar'


def test_create_summary_invalid_json(test_app_with_db):
    response = test_app_with_db.post('/summaries/', data=json.dumps({}))
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'loc': ['body', 'url'],
                'msg': 'field required',
                'type': 'value_error.missing',
            }
        ]
    }

    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'invalid://url'}))
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'URL scheme not permitted'


def test_read_summary(test_app_with_db):
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo.bar'}))
    assert response.status_code == 201
    summary_id = response.json()['id']

    response = test_app_with_db.get(f'/summaries/{summary_id}/')
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict['id'] == summary_id
    assert response_dict['url'] == 'https://foo.bar'
    assert response_dict['summary']
    assert response_dict['created_at']


def test_read_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.get('/summaries/999/')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Summary not found'

    response = test_app_with_db.get('/summaries/0')
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'loc': ['path', 'summary_id'],
                'msg': 'ensure this value is greater than 0',
                'type': 'value_error.number.not_gt',
                'ctx': {'limit_value': 0},
            }
        ]
    }


def test_read_all_summaries(test_app_with_db):
    added_summaries = []
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo1.bar'}))
    assert response.status_code == 201
    added_summaries.append(response.json()['id'])
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo2.bar'}))
    assert response.status_code == 201
    added_summaries.append(response.json()['id'])

    response = test_app_with_db.get('/summaries/')
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda x: x['id'] in added_summaries, response_list))) == 2


def test_remove_summary(test_app_with_db):
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo.bar'}))
    assert response.status_code == 201
    summary_id = response.json()['id']

    response = test_app_with_db.delete(f'/summaries/{summary_id}/')
    assert response.status_code == 200
    assert response.json() == {'id': summary_id, 'url': 'https://foo.bar'}


def test_remove_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.delete('/summaries/999/')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Summary not found'


def test_update_summary(test_app_with_db):
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo.bar'}))
    assert response.status_code == 201
    summary_id = response.json()['id']

    response = test_app_with_db.put(
        f'/summaries/{summary_id}/', data=json.dumps({'url': 'https://foo.bar', 'summary': 'Updated summary'})
    )
    assert response.status_code == 200

    response = test_app_with_db.get(f'/summaries/{summary_id}/')
    assert response.status_code == 200
    summary_info = response.json()
    assert summary_info['id'] == summary_id
    assert summary_info['url'] == 'https://foo.bar'
    assert summary_info['summary'] == 'Updated summary'
    assert summary_info['created_at']


def test_update_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.put(
        '/summaries/999/', data=json.dumps({'url': 'https://foo.bar', 'summary': 'Updated summary'})
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'Summary not found'


def test_update_summary_invalid_json(test_app_with_db):
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo.bar'}))
    assert response.status_code == 201
    summary_id = response.json()['id']

    response = test_app_with_db.put(f'/summaries/{summary_id}/', data=json.dumps({}))
    assert response.status_code == 422
    assert response.json()['detail'] == [
        {'loc': ['body', 'url'], 'msg': 'field required', 'type': 'value_error.missing'},
        {'loc': ['body', 'summary'], 'msg': 'field required', 'type': 'value_error.missing'},
    ]


def test_update_summary_invalid_keys(test_app_with_db):
    response = test_app_with_db.post('/summaries/', data=json.dumps({'url': 'https://foo.bar'}))
    assert response.status_code == 201
    summary_id = response.json()['id']

    response = test_app_with_db.put(f'/summaries/{summary_id}/', data=json.dumps({'url': 'https://foo.bar'}))
    assert response.status_code == 422
    assert response.json()['detail'] == [
        {'loc': ['body', 'summary'], 'msg': 'field required', 'type': 'value_error.missing'}
    ]
