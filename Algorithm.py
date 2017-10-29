from pyqtree import Index
from Dot import Dot

def create_quadtree(file):
    # go through the file and create a dot object for each line and add it to a list
    dot_list = []

    for line in file:
        line = line.split()
        x = float(line[0])
        y = float(line[1])
        label = line[2]
        dot_list.append(Dot(label, (x, y, x, y)))
    file.close()

    # add all dots to the quadtree
    spindex = Index(bbox=(0, 0, 1, 1))
    for dot in dot_list:
        spindex.insert(dot, dot.bbox)

    return spindex

def algorithm(input, grid_size, d_max, k_min):
    d_max = d_max/grid_size
    # insert the dot_list into a quadtree
    file = open(input, "r")
    nr_data_point = int(next(file))
    quad_tree = create_quadtree(file)
    output_quadtree = Index(bbox=(0, 0, 1, 1))

    #determine k
    counter = 0
    for y in range(grid_size):
        for x in range(grid_size):
            current_cell = (x/grid_size, y/grid_size, (x+1)/grid_size, (y+1)/grid_size)
            intersection = quad_tree.intersect(current_cell)
            if len(intersection) >= k_min * int(nr_data_point/(grid_size*grid_size)):
                counter+=1
    k = int((nr_data_point/counter) * 0.9)

    # loop through the grid
    for y in range(grid_size):
        for x in range(grid_size):
            # make the rectangle to find dots in
            current_cell = (max(x/grid_size - d_max, 0), max(y/grid_size - d_max, 0), min((x+1)/grid_size + d_max, 1), min((y+1)/grid_size + d_max, 1))
            # intersect on this rectangle
            intersection = quad_tree.intersect(current_cell)

            # count the number of each label in the intersection
            label_count = {}
            for dot in intersection:
                if dot.label in label_count:
                    label_count[dot.label] += 1
                else:
                    label_count[dot.label] = 1

            # find the lowest frequency label that can be made into a new dot
            while len(label_count) > 0:
                min_label = min(label_count, key=label_count.get)
                # if we can make it into a new dot we remove the labels and enter a new one
                if label_count[min_label] >= k_min * k:
                    cell_center = Dot(min_label, bbox=(
                                          (x / grid_size + (x + 1) / grid_size) / 2,
                                          (y / grid_size + (y + 1) / grid_size) / 2,
                                          (x / grid_size + (x + 1) / grid_size) / 2,
                                          (y / grid_size + (y + 1) / grid_size) / 2)
                                         )
                    output_quadtree.insert(cell_center, cell_center.bbox)
                    # now remove the dots that it intersected with going by minimum distance up to k
                    if label_count[min_label] >= k:
                        sorted_distance_list = sorted_distance(intersection, cell_center, k, min_label)
                        for dot in sorted_distance_list:
                            quad_tree.remove(dot, dot.bbox)
                    else:
                        for dot in intersection:
                            if(dot.label == min_label):
                                quad_tree.remove(dot, dot.bbox)
                    break
                else:
                    # if there werent enough labels of a color remove them from the dict.
                    del label_count[min_label]

    # write the output to file
    create_output(output_quadtree, k, grid_size)

# return the k dots with the good label closest to the cell center
def sorted_distance(dot_list, cell_center, k, min_label):
    # map each dot to a distance value
    dots = {}
    for dot in dot_list:
        if(dot.label == min_label):
            dots[dot] = distance(dot, cell_center)

    # retrieve the k lowest distance dots.
    k_dots = set()
    for i in range(k):
        min_dot = min(dots, key=dots.get)
        k_dots.add(min_dot)
        del dots[min_dot]

    return k_dots

# calculate the Manhattan distance between 2 dots
def distance(dot, cell_center):
    dot_x = dot.bbox[0]
    dot_y = dot.bbox[1]
    cell_center_x = cell_center.bbox[0]
    cell_center_y = cell_center.bbox[1]
    distance = abs(dot_x - cell_center_x) + abs(dot_y - cell_center_y)
    return distance

def create_output(quad_tree, k, grid_size):
    output = open("output.txt", "w")
    output.write(str(k) + '\n')
    #go through all the cells
    for y in range(grid_size):
        for x in range(grid_size):
            # make the rectangle to find dots in
            current_cell = (x/grid_size, y/grid_size, (x+1)/grid_size, (y+1)/grid_size)
            # intersect on this rectangle, cell should only contain 1 entry
            cell = quad_tree.intersect(current_cell)
            if len(cell) == 0:
                if x < grid_size - 1:
                    output.write(",")
            if len(cell) == 1:
                if x < grid_size - 1:
                    output.write(next(iter(cell)).label + ",")
                else:
                    output.write(next(iter(cell)).label)
        output.write("\n")
    output.close()

algorithm("checker-50000-4-42.txt", 17, 0, 0.75)









