import os

import face_recognition
import numpy
from PIL import Image, ImageDraw
from flask import jsonify

from static.application.App import App


class Recognition:
    @staticmethod
    def fire(token, filename):
        _app = App()
        user_id = _app.get_user_id(token)

        if not user_id:
            _app.close()
            return jsonify({'status': 400, 'message': ["UNKNOWN_TOKEN"], 'result': None})
        else:
            upload_path = "./private/cache/"
            unknown_image = face_recognition.load_image_file(upload_path + filename)
            unknown_face_locations = face_recognition.face_locations(unknown_image)
            if len(unknown_face_locations) == 0:
                return jsonify({'status': 400, 'message': ["NOTFOUND_UPLOAD_FACE"], 'result': None})
            else:
                unknown_face_encodings = face_recognition.face_encodings(unknown_image)

                # child
                child_face = _app.get_child_face(user_id)
                child_file_list = []
                for child in child_face:
                    child_file_list.append(child["file_name"])
                if len(child_file_list) > 0:
                    _app.download(child_file_list, child=True)

                # friend
                friend_face = _app.get_friend_face(user_id)
                friend_file_list = []
                for friend in friend_face:
                    friend_file_list.append(friend["file_name"])
                if len(friend_file_list) > 0:
                    _app.download(friend_file_list, friend=True)

                face_model = []
                for face in child_face:
                    face_model.append({
                        "type": "child",
                        "user_name": face["user_name"],
                        "file_name": face["file_name"],
                        "file_path": "./private/child-face/" + face["file_name"]
                    })
                for face in friend_face:
                    face_model.append({
                        "type": "friend",
                        "user_name": face["user_name"],
                        "file_name": face["file_name"],
                        "file_path": "./private/friend-face/" + face["file_name"]
                    })

                if len(face_model) == 0:
                    return jsonify({'status': 400, 'message': ["NOTFOUND_FACE_IMAGE"], 'result': None})
                else:
                    known_face_encodings = []
                    known_face_names = []
                    for face in face_model:
                        image = face_recognition.load_image_file(face["file_path"])
                        face_locations = face_recognition.face_locations(image)
                        if len(face_locations) > 0:
                            face_encodings = face_recognition.face_encodings(image)[0]
                            known_face_encodings.append(face_encodings)
                            known_face_names.append(face["user_name"])

                    if len(known_face_encodings) == 0:
                        return jsonify({'status': 400, 'message': ["NOTFOUND_KNOWN_FACE"], 'result': None})
                    else:
                        pil_image = Image.fromarray(unknown_image)
                        draw = ImageDraw.Draw(pil_image)
                        match_name = []
                        for (top, right, bottom, left), unknown_face_encoding \
                                in zip(unknown_face_locations, unknown_face_encodings):
                            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255), width=10)

                            matches = face_recognition.compare_faces(
                                known_face_encodings,
                                unknown_face_encoding,
                                tolerance=0.5
                            )

                            face_distances = face_recognition.face_distance(known_face_encodings, unknown_face_encoding)
                            best_match_index = numpy.argmin(face_distances)
                            if matches[best_match_index]:
                                match_name.append(known_face_names[best_match_index])
                                draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0), width=10)

                        # plt.imshow(pil_image)
                        # plt.show()

                        if os.path.exists(upload_path + filename):
                            os.remove(upload_path + filename)

                        pil_image.save(upload_path + filename)

                        _app.close()

                        return jsonify({'status': 200, 'message': None, 'result': {'match_user': match_name}})
