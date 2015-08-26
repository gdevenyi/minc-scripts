#!/usr/bin/env python
#
# Convert between different mesh file formats
#
# author: jan.scholz@mouseimaging.ca
# original version: 2015-03-25
# based on: http://www.cfd-online.com/Forums/openfoam-meshing/86416-vtk-openfoam-something-else-can-reach-after-openfoam.html

import vtk
from optparse import OptionParser
from os import path


class MyParser(OptionParser):
    """alow adding usage examples in epilog"""
    def format_epilog(self, formatter):
        return '\n' + self.epilog + '\n'


def readMeshFile(filename, clean=True, verbose=False):
    """Read mesh file.
    The input format is determined by file name extension.
    Polygons get split into triangles to support various restrictive output
    formats.
    If clean, degenerate data gets removed."""

    informat = path.splitext(options.infilename)[1].strip('.')
    # set reader based on filename extension
    if informat=='stl':
        reader = vtk.vtkSTLReader()
    elif informat=='vtk':
        reader = vtk.vtkPolyDataReader()
    elif informat=='obj':
        reader = vtk.vtkMNIObjectReader()
    elif informat=='ply':
        reader = vtk.vtkPLYReader()
    #elif informat=='tag':
    #    reader = vtk.vtkMNITagPointReader()
    else:
        raise ValueError('cannot read input format: ' + informat)
    reader.SetFileName(filename)
    reader.Update()

    if verbose:
        print "read %i polygons from file %s" % \
                               (reader.GetOutput().GetNumberOfPolys(), filename)

    # merge duplicate points, and/or remove unused points and/or remove degenerate cells
    if clean:
        polydata = vtk.vtkCleanPolyData()
        polydata.SetInputConnection(reader.GetOutputPort())
        poly_data_algo = polydata
        if verbose:
            print "cleaned poly data"
    else:
        poly_data_algo = reader

    # convert input polygons and strips to triangles
    triangles = vtk.vtkTriangleFilter()
    triangles.SetInputConnection(poly_data_algo.GetOutputPort())

    if verbose:
        print "finished reading", filename

    return triangles


def writeMeshFile(triangles, filename, binary=True, verbose=False):
    """Write mesh file.
    The output format is determined by file name extension. Files can be written
    in binary (default) and ASCII format."""

    outformat = path.splitext(options.outfilename)[1].strip('.')
    # set writer based on filename extension
    if outformat=='stl':
        write = vtk.vtkSTLWriter()
    elif outformat=='vtk':
        write = vtk.vtkPolyDataWriter()
    elif outformat=='obj':
        write = vtk.vtkMNIObjectWriter()
    elif outformat=='ply':
        write = vtk.vtkPLYWriter()
    elif outformat=='tag':
        write = vtk.vtkMNITagPointWriter()
    else:
        raise ValueError('cannot write outpur format' + outformat)
    write.SetInputConnection(triangles.GetOutputPort())

    if outformat!='tag':
        if binary:
            if verbose: print 'setting ouptut to binary'
            write.SetFileTypeToBinary()
        else:
            if verbose: print 'setting ouptut to ascii'
            write.SetFileTypeToASCII()

    write.SetFileName(filename)
    err = write.Write()
    if err != 1:
        raise IOError('failed to write')

    if verbose:
        print "wrote", filename
    pass



if __name__ == "__main__":
    usage = """usage: %prog [-h/--help] -i INFILE -o OUTFILE"""

    description = """Convert between mesh file formats.
    Currently supports reading and writing of STL, VTK, OBJ (BIC object)"""
    epilog = "Example:\n  " + \
        path.basename(__file__) + " -v --ascii -i foo.vtk -o bar.stl"

    parser = MyParser(usage=usage, description=description, epilog=epilog)

    parser.add_option("-i", "--input", dest="infilename",
                      help="no help",
                      type='string', default="")
    parser.add_option("-o", "--output", dest="outfilename",
                      help="no help",
                      type='string', default="")
    parser.add_option("-a", "--ascii", dest="binary",
                      help="save in ascii format",
                      action="store_false", default=True)
    parser.add_option("--noclean", dest="clean",
                      help="remove degenerate data",
                      action="store_false", default=True)
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="more verbose output",
                      action="store_true", default=False)

    (options, args) = parser.parse_args()

    if options.infilename is '':
        parser.error('INFILE not specified (-i)')

    if options.outfilename is '':
        parser.error('OUTFILE not specified (-o)')

    if not path.exists(options.infilename):
        parser.error('could not find INFILE')

    outpath = path.dirname(options.outfilename)
    if outpath and not path.exists(outpath):
        parser.error('output directory does not exist: ' + outpath)

    triangles = readMeshFile(options.infilename, clean=options.clean, verbose=options.verbose)

    writeMeshFile(triangles, options.outfilename, binary=options.binary,
                  verbose=options.verbose)
