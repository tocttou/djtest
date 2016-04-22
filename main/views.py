import os
import cv2
import json
import glob
import numpy as np
from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt


#####################################################
# view for the home page (/home)
#####################################################

def home(request):
    return render(request, 'index.html',
                  {
                      'title': 'OpenCV Online'
                  })


#####################################################
# view for cache request (/cached)
#####################################################

@csrf_exempt
def cached(request):
    if request.method == 'POST':
        if request.is_ajax():
            data = request.body
            dir_id = data.split('=')[1]
            all_images = glob.glob('/tmp/{}/*.jpg'.format(dir_id)) + \
                         glob.glob('/tmp/{}/*.png'.format(dir_id))
            for index, image in enumerate(all_images):
                all_images[index] = image.split('/')[-1]\
                .strip('.jpg').strip('.png')
            return StreamingHttpResponse(json.dumps(all_images), content_type="application/json")
        return StreamingHttpResponse("Malformed request")
    else:
        return StreamingHttpResponse('The request should be POST bud')


#####################################################
# view for pipeline builder (/runner)
#####################################################

class Filter:
    def __init__(self, **kwargs):
        self.node_index = kwargs['node_index']
        self.parents_node = kwargs['parents_node']
        self.node_data_array = kwargs['node_data_array']
        self.dir_id = kwargs['dir_id']
        self.function_map = {
            'gBlur': self.gblur,
            'mBlur': self.mblur,
            'grayscale': self.grayscale,
            'not': self.bitwise_not,
            'canny': self.auto_canny,
            'laplacian': self.laplacian,
            'XOR': self.XOR,
            'AND': self.AND,
            'OR': self.OR,
            'ADD': self.ADD
        }

    # helper functions to load and save images
    @staticmethod
    def save_image(file_id, dir_id, data):
        try:
            all_images = glob.glob('/tmp/{}/*.jpg'.format(dir_id)) + \
                         glob.glob('/tmp/{}/*.png'.format(dir_id))
            all_ids = {}
            for index, image in enumerate(all_images):
                file_name = image.split('/')[-1]\
                        .strip('.jpg').strip('.png')
                file_type = image.split('/')[-1]\
                        .split('.')[1]
                all_ids[file_name] = file_type

            file_path = ''
            file_type = ''

            if file_id in all_ids:
                file_type = all_ids[file_id]
                file_path = "/tmp/{}/{}.{}".format(dir_id, file_id, file_type)
            else:
                if not os.path.exists('/tmp/' + str(dir_id)):
                    os.makedirs('/tmp/' + str(dir_id))

                file_type = 'png'
                if 'jpeg' in data.split(',')[0]:
                    file_type = 'jpg'
                data = data.split(',')[1]
                file_path = "/tmp/{}/{}.{}".format(dir_id, file_id, file_type)
                f = open(file_path, "wb")
                f.write(data.decode('base64'))
                f.close()

            return [file_path, file_type]
        except:
            return False

    @staticmethod
    def load_image(file_path, file_type):
        try:
            src = ''
            if file_type == 'jpg':
                src += 'data:image/jpeg;base64,'
            elif file_type == 'png':
                src += 'data:image/png;base64,i'
            with open(file_path, "rb") as f:
                data = f.read()
                src += data.encode("base64")
            return src
        except:
            return False

    def make_new_src(self, path, file_type, img):
        cv2.imwrite(path, img)
        new_src = Filter.load_image(path, file_type)
        if new_src:
            self.node_data_array[self.node_index]['src'] = new_src
            self.node_data_array[self.node_index]['calculated'] = 'yes'
            return self.node_data_array
        else:
            return False

    # filter functions
    def grayscale(self):
        image_path = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        if image_path:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path[1]
            )

            # function goes here
            img = cv2.imread(image_path[0])
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path[1],
                img
            )
        else:
            return False

    def gblur(self):
        image_path = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        if image_path:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path[1]
            )

            # function goes here
            img = cv2.imread(image_path[0])
            img = cv2.GaussianBlur(img, (5, 5), 0)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path[1],
                img
            )
        else:
            return False

    def mblur(self):
        image_path = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        if image_path:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path[1]
            )

            # function goes here
            img = cv2.imread(image_path[0])
            img = cv2.medianBlur(img, 5)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path[1],
                img
            )
        else:
            return False

    def bitwise_not(self):
        image_path = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        if image_path:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path[1]
            )

            # function goes here
            img = cv2.imread(image_path[0])
            img = cv2.bitwise_not(img)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path[1],
                img
            )
        else:
            return False

    def auto_canny(self):
        image_path = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        if image_path:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path[1]
            )

            # function goes here
            img = cv2.imread(image_path[0])
            v = np.median(img)
            sigma = 0.33
            lower = int(max(0, (1.0 - sigma) * v))
            upper = int(min(255, (1.0 + sigma) * v))
            img = cv2.Canny(img, lower, upper)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path[1],
                img
            )
        else:
            return False

    def laplacian(self):
        image_path = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        if image_path:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path[1]
            )

            # function goes here
            img = cv2.imread(image_path[0])
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img = cv2.GaussianBlur(img, (3, 3), 0)
            img = cv2.Laplacian(img, cv2.CV_64F)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path[1],
                img
            )
        else:
            return False

    def ADD(self):
        image_path1 = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        image_path2 = Filter.save_image(
            self.parents_node[1]['key'],
            self.dir_id,
            self.parents_node[1]['src']
        )
        if image_path1 and image_path2:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path1[1]
            )

            # function goes here
            img1 = cv2.imread(image_path1[0])
            img2 = cv2.imread(image_path2[0])
            img = cv2.add(img1, img2)
            # img = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path1[1],
                img
            )
        else:
            return False

    def XOR(self):
        image_path1 = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        image_path2 = Filter.save_image(
            self.parents_node[1]['key'],
            self.dir_id,
            self.parents_node[1]['src']
        )
        if image_path1 and image_path2:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path1[1]
            )

            # function goes here
            img1 = cv2.imread(image_path1[0])
            img2 = cv2.imread(image_path2[0])
            img = cv2.bitwise_xor(img1, img2)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path1[1],
                img
            )
        else:
            return False

    def AND(self):
        image_path1 = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        image_path2 = Filter.save_image(
            self.parents_node[1]['key'],
            self.dir_id,
            self.parents_node[1]['src']
        )
        if image_path1 and image_path2:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path1[1]
            )

            # function goes here
            img1 = cv2.imread(image_path1[0])
            img2 = cv2.imread(image_path2[0])
            img = cv2.bitwise_and(img1, img2)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path1[1],
                img
            )
        else:
            return False

    def OR(self):
        image_path1 = Filter.save_image(
            self.parents_node[0]['key'],
            self.dir_id,
            self.parents_node[0]['src']
        )
        image_path2 = Filter.save_image(
            self.parents_node[1]['key'],
            self.dir_id,
            self.parents_node[1]['src']
        )
        if image_path1 and image_path2:
            temp_save_path = '/tmp/{}/{}.{}'.format(
                self.dir_id,
                self.node_data_array[self.node_index]['key'],
                image_path1[1]
            )

            # function goes here
            img1 = cv2.imread(image_path1[0])
            img2 = cv2.imread(image_path2[0])
            img = cv2.bitwise_or(img1, img2)
            # function ends here

            return self.make_new_src(
                temp_save_path,
                image_path1[1],
                img
            )
        else:
            return False


# this function evaluates the node image
# returns the modified nodeDataArray
# with embedded new image
def evaluate(node_index, parents, node_data_array, dir_id):
    parents_node = []
    parents_id = [x['from'] for x in parents]
    for node in node_data_array:
        if node['key'] in parents_id:
            parents_node.append(node)
    for parent in parents_node:
        if parent['calculated'] == 'no':
            return False
    func_name = parents[0]['function']
    eval_node = Filter(
        node_index=node_index,
        parents_node=parents_node,
        node_data_array=node_data_array,
        dir_id=dir_id
    )
    new_node_data_array = eval_node.function_map[func_name]()
    return new_node_data_array


# this function parses the incoming json
# data and runs a recursive call to evaluate
# all the nodes [passes the new nodeDataArray
# returned from evaluate to itself for more
# evaluation passes until all nodes have a
# 'completed' = yes]
def parser(node_data_array, link_data_array, dir_id):
    for node_index, node in enumerate(node_data_array):
        if node['calculated'] == 'no':
            parents = []
            for link in link_data_array:
                if link['to'] == node['key']:
                    parents.append(link)
            new_node_data_array = evaluate(node_index, parents, node_data_array, dir_id)

            # recursive call to parser to parse all the elements

            return parser(new_node_data_array, link_data_array, dir_id)
    return node_data_array


@csrf_exempt
def runner(request):
    if request.method == 'POST':
        if request.is_ajax():
            data = json.loads(request.body)
            link_data_array = data['linkDataArray']
            node_data_array = data['nodeDataArray']
            dir_id = data['dir_id']
            new_node_data_array = parser(node_data_array, link_data_array, dir_id)
            if new_node_data_array:
                return StreamingHttpResponse(json.dumps(new_node_data_array), content_type="application/json")
            else:
                return StreamingHttpResponse('cannot complete request')
        return StreamingHttpResponse("Malformed request")
    else:
        return StreamingHttpResponse('The request should be POST bud')
