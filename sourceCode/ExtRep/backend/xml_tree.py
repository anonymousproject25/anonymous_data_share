from backend.tree_node import TreeNode


class XmlTree(object):
    def __init__(self, root_node):
        self.nodes = []
        self.root_node = root_node

        self.id = -1
        self.layers = {}

        self.leaf_nodes = []
        self.branch_nodes = []

        self.leaf_resource_id_count = {}
        self.leaf_text_count = {}
        self.leaf_content_count = {}

        self.branch_resource_id_count = {}
        self.branch_text_count = {}
        self.branch_content_count = {}

    def dfs(self, node, parent):
        if 'package' in node.attrib and node.attrib['package'] == 'com.android.systemui':
            return

        node.parent = parent

        node.idx = self.id
        node.get_bounds()
        self.nodes.append(node)
        self.id += 1

        if node.layer not in self.layers:
            self.layers[node.layer] = [node.idx]
        else:
            self.layers[node.layer].append(node.idx)

        children_xml_node = node.xml_node.getchildren()

        if len(children_xml_node) == 0:
            return

        class_count = {}
        for xml_node in children_xml_node:

            if 'package' in xml_node.attrib and xml_node.attrib['package'] == 'com.android.systemui':
                continue

            child_node = TreeNode(xml_node, node.layer + 1)
            class_name = child_node.attrib['class']

            if class_name not in class_count.keys():
                class_count[class_name] = 1
                child_node.class_index = 1
                class_count[class_name] += 1
            else:
                child_node.class_index = class_count[class_name]
                class_count[class_name] += 1

            node.children.append(child_node)

        for child_node in node.children:
            self.dfs(child_node, node)

    def get_nodes_full_xpath(self, node):
        if node.parent is None:
            node.full_xpath = '//'
            return "//"

        class_name = node.attrib['class']
        xpath_class_index = class_name + "[" + str(node.class_index) + "]"

        parent_node = node.parent

        parent_full_xpath = parent_node.full_xpath

        if parent_node.full_xpath == '':
            parent_full_xpath = self.get_nodes_full_xpath(parent_node)

        if parent_full_xpath != '//':
            full_xpath = parent_full_xpath + '/' + xpath_class_index
            node.full_xpath = full_xpath
            return full_xpath

        else:
            full_xpath = parent_full_xpath + xpath_class_index
            node.full_xpath = full_xpath
            return full_xpath

    def get_nodes_stat(self):
        for node in self.leaf_nodes:
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            if resource_id not in self.leaf_resource_id_count:
                self.leaf_resource_id_count[resource_id] = 1
            else:
                self.leaf_resource_id_count[resource_id] += 1

            if text not in self.leaf_text_count:
                self.leaf_text_count[text] = 1
            else:
                self.leaf_text_count[text] += 1

            if content not in self.leaf_content_count:
                self.leaf_content_count[content] = 1
            else:
                self.leaf_content_count[content] += 1

        for node in self.branch_nodes:
            if node.full_xpath == '//':
                continue
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            if resource_id not in self.branch_resource_id_count:
                self.branch_resource_id_count[resource_id] = 1
            else:
                self.branch_resource_id_count[resource_id] += 1

            if text not in self.branch_text_count:
                self.branch_text_count[text] = 1
            else:
                self.branch_text_count[text] += 1

            if content not in self.branch_content_count:
                self.branch_content_count[content] = 1
            else:
                self.branch_content_count[content] += 1

    def get_nodes_ans(self, node):
        if node.full_xpath == '//':
            return None

        if len(node.xpath) > 1:
            return node
        else:
            return self.get_nodes_ans(node.parent)

    def get_nodes_xpath_by_ans(self, cur_node):
        ans_node = self.get_nodes_ans(cur_node.parent)

        if ans_node is None:
            return ''

        node_class_name = cur_node.attrib['class']
        node_resource_id = cur_node.attrib['resource-id']
        node_text = cur_node.attrib['text']
        node_content = cur_node.attrib['content-desc']

        resource_id_count = {}
        text_count = {}
        content_count = {}

        if cur_node.children:
            for node in ans_node.descendants:
                if node.children:
                    resource_id = node.attrib['resource-id']
                    text = node.attrib['text']
                    content = node.attrib['content-desc']

                    if resource_id not in resource_id_count:
                        resource_id_count[resource_id] = 1
                    else:
                        resource_id_count[resource_id] += 1

                    if text not in text_count:
                        text_count[text] = 1
                    else:
                        text_count[text] += 1

                    if content not in content_count:
                        content_count[content] = 1
                    else:
                        content_count[content] += 1
        else:
            for node in ans_node.descendants:
                if not node.children:
                    resource_id = node.attrib['resource-id']
                    text = node.attrib['text']
                    content = node.attrib['content-desc']

                    if resource_id not in resource_id_count:
                        resource_id_count[resource_id] = 1
                    else:
                        resource_id_count[resource_id] += 1

                    if text not in text_count:
                        text_count[text] = 1
                    else:
                        text_count[text] += 1

                    if content not in content_count:
                        content_count[content] = 1
                    else:
                        content_count[content] += 1

        if node_resource_id in resource_id_count and \
                resource_id_count[node_resource_id] == 1:
            xpath = ans_node.xpath[1] + '/' + node_class_name + '[' + '@resource-id=' + '"' + resource_id + '"' + ']'
            return xpath

        if node_text in text_count and \
                text_count[node_text] == 1:
            xpath = ans_node.xpath[1] + '/' + node_class_name + '[' + '@text=' + '"' + text + '"' + ']'
            return xpath

        if node_content in content_count and \
                content_count[node_content] == 1:
            xpath = ans_node.xpath[1] + '/' + node_class_name + '[' + '@content=' + '"' + text + '"' + ']'
            return xpath

        return ''

    def get_branch_nodes_xpath(self):
        self.branch_nodes.sort(key=lambda x: x.layer)

        for node in self.branch_nodes:

            node.xpath.append(node.full_xpath)

            if node.full_xpath == '//':
                continue

            class_name = node.attrib['class']
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            if resource_id in self.branch_resource_id_count and self.branch_resource_id_count[resource_id] == 1:
                xpath = '//' + class_name + '[' + '@resource-id=' + '"' + resource_id + '"' + ']'
                node.xpath.append(xpath)
                continue

            if text in self.branch_text_count and self.branch_text_count[text] == 1:
                xpath = '//' + class_name + '[' + '@text=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)
                continue

            if content in self.branch_content_count and self.branch_content_count[content] == 1:
                xpath = '//' + class_name + '[' + '@content=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)
                continue

            id_text_count = 0
            id_content_count = 0
            text_content_count = 0
            id_text_content_count = 0

            for tmp_node in self.branch_nodes:
                if tmp_node.full_xpath == '//':
                    continue
                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text:
                    id_text_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['content-desc'] == content:
                    id_content_count += 1

                if tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    text_content_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    id_text_content_count += 1

            if id_text_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' + ']')
                node.xpath.append(xpath)
                continue

            if id_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)
                continue

            if text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)
                continue

            if id_text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)
                continue

            xpath = self.get_nodes_xpath_by_ans(node)
            if xpath != '':
                node.xpath.append(xpath)

    def get_leaf_nodes_xpath(self):

        for node in self.leaf_nodes:
            node.xpath.append(node.full_xpath)

            class_name = node.attrib['class']
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            if resource_id in self.leaf_resource_id_count and self.leaf_resource_id_count[resource_id] == 1:
                xpath = '//' + class_name + '[' + '@resource-id=' + '"' + resource_id + '"' + ']'
                node.xpath.append(xpath)

            if text in self.leaf_text_count and self.leaf_text_count[text] == 1:
                xpath = '//' + class_name + '[' + '@text=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)

            if content in self.leaf_content_count and self.leaf_content_count[content] == 1:
                xpath = '//' + class_name + '[' + '@content=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)

            id_text_count = 0
            id_content_count = 0
            text_content_count = 0
            id_text_content_count = 0

            for tmp_node in self.leaf_nodes:
                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text:
                    id_text_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['content-desc'] == content:
                    id_content_count += 1

                if tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    text_content_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    id_text_content_count += 1

            if id_text_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' + ']')
                node.xpath.append(xpath)

            if id_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)

            if text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)

            if id_text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)

            if len(node.xpath) == 1:
                xpath = self.get_nodes_xpath_by_ans(node)
                if xpath != '':
                    node.xpath.append(xpath)

    def get_nodes_xpath(self):
        self.get_branch_nodes_xpath()
        self.get_leaf_nodes_xpath()

    def parse_nodes(self):
        self.dfs(self.root_node, None)

        for node in self.nodes:
            self.get_nodes_full_xpath(node)
            node.get_descendants(node)

        for node in self.nodes[1:]:
            node.attrib['text'] = node.attrib['text'].replace(' ', '')
            node.attrib['content-desc'] = node.attrib['content-desc'].replace(' ', '')
            if not node.children:
                self.leaf_nodes.append(node)
            else:
                if 'roation' not in node.attrib.keys():
                    self.branch_nodes.append(node)

        self.get_nodes_stat()
        self.get_nodes_xpath()

        self.nodes = self.nodes[1:]

        tmp_nodes = []
        tmp_leaf_nodes = []
        tmp_branch_nodes = []
        for node in self.nodes:
            x1, y1, x2, y2 = node.parse_bounds()

            if x1 < x2 and y1 < y2:
                if not node.children:
                    tmp_leaf_nodes.append(node)
                else:
                    tmp_branch_nodes.append(node)

                tmp_nodes.append(node)

        self.nodes = tmp_nodes
        self.leaf_nodes = tmp_leaf_nodes
        self.branch_nodes = tmp_branch_nodes

        return self.nodes

    # don't remove spaces
    def parse_nodes_patch(self):
        self.dfs(self.root_node, None)

        for node in self.nodes:
            self.get_nodes_full_xpath(node)
            node.get_descendants(node)

        for node in self.nodes[1:]:
            node.attrib['text'] = node.attrib['text']
            node.attrib['content-desc'] = node.attrib['content-desc']
            if not node.children:
                self.leaf_nodes.append(node)
            else:
                if 'roation' not in node.attrib.keys():
                    self.branch_nodes.append(node)

        self.get_nodes_stat()
        self.get_nodes_xpath()

        self.nodes = self.nodes[1:]

        tmp_nodes = []
        tmp_leaf_nodes = []
        tmp_branch_nodes = []
        for node in self.nodes:
            x1, y1, x2, y2 = node.parse_bounds()

            if x1 < x2 and y1 < y2:
                if not node.children:
                    tmp_leaf_nodes.append(node)
                else:
                    tmp_branch_nodes.append(node)

                tmp_nodes.append(node)

        self.nodes = tmp_nodes
        self.leaf_nodes = tmp_leaf_nodes
        self.branch_nodes = tmp_branch_nodes

        return self.nodes

def parse_nodes(root):
    root_node = TreeNode(root, 0)
    xml_tree = XmlTree(root_node)
    nodes = xml_tree.parse_nodes()

    return nodes

def parse_nodes_patch(root):
    root_node = TreeNode(root, 0)
    xml_tree = XmlTree(root_node)
    nodes = xml_tree.parse_nodes_patch()

    return nodes
