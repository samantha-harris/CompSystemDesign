import pickle, logging
import argparse

from memoryfs import *
import os.path

## This class implements an interactive shell to navigate the file system

class FSShell():
  def __init__(self, file):
    # cwd stored the inode of the current working directory
    # we start in the root directory
    self.cwd = 0
    self.FileObject = file

  # implements cd (change directory)
  def cd(self, dir):
    i = self.FileObject.Lookup(dir,self.cwd)
    if i == -1:
      print ("Error: not found\n")
      return -1
    inobj = InodeNumber(self.FileObject.RawBlocks,i)
    inobj.InodeNumberToInode()
    if inobj.inode.type != INODE_TYPE_DIR:
      print ("Error: not a directory\n")
      return -1
    self.cwd = i

  # implements ls (lists files in directory)
  def ls(self):
  # your solution goes here

  # implements cat (print file contents)
  def cat(self, filename):
  # your solution goes here

  # implements showblock (log block n contents)
  def showblock(self, n):

    try:
      n = int(n)
    except ValueError:
      print('Error: ' + n + ' not a valid Integer')
      return -1

    if n < 0 or n >= TOTAL_NUM_BLOCKS:
      print('Error: block number ' + str(n) + ' not in valid range [0, ' + str(TOTAL_NUM_BLOCKS - 1) + ']')
      return -1
    logging.info('Block (string) [' + str(n) + '] : ' + str((self.FileObject.RawBlocks.Get(n).decode(encoding='UTF-8',errors='ignore'))))
    logging.info('Block (hex) [' + str(n) + '] : ' + str((self.FileObject.RawBlocks.Get(n).hex())))
    return 0

  # implements showinode (log inode i contents)
  def showinode(self, i):

    try:
      i = int(i)
    except ValueError:
      print('Error: ' + i + ' not a valid Integer')
      return -1

    if i < 0 or i >= MAX_NUM_INODES:
      print('Error: inode number ' + str(i) + ' not in valid range [0, ' + str(MAX_NUM_INODES - 1) + ']')
      return -1

    inobj = InodeNumber(self.FileObject.RawBlocks, i)
    inobj.InodeNumberToInode()
    inode = inobj.inode
    inode.Print()
    return 0

  # implements showfsconfig (log fs config contents)
  def showfsconfig(self):
    self.FileObject.RawBlocks.PrintFSInfo()
    return 0

  # implements load (load the specified dump file)
  def load(self, dumpfilename):
    if not os.path.isfile(dumpfilename):
      print("Error: Please provide valid file")
      return -1
    self.FileObject.RawBlocks.LoadFromDisk(dumpfilename)
    self.cwd = 0
    return 0

  # implements save (save the file system contents to specified dump file)
  def save(self, dumpfilename):
    self.FileObject.RawBlocks.DumpToDisk(dumpfilename)
    return 0

  def Interpreter(self):
    while (True):
      command = input("[cwd=" + str(self.cwd) + "]:")
      splitcmd = command.split()
      if len(splitcmd) == 0:
        continue
      elif splitcmd[0] == "cd":
        if len(splitcmd) != 2:
          print ("Error: cd requires one argument")
        else:
          self.cd(splitcmd[1])
      elif splitcmd[0] == "cat":
        if len(splitcmd) != 2:
          print ("Error: cat requires one argument")
        else:
          self.cat(splitcmd[1])
      elif splitcmd[0] == "ls":
        self.ls()
      elif splitcmd[0] == "showblock":
        if len(splitcmd) != 2:
          print ("Error: showblock requires one argument")
        else:
          self.showblock(splitcmd[1])
      elif splitcmd[0] == "showinode":
        if len(splitcmd) != 2:
          print ("Error: showinode requires one argument")
        else:
          self.showinode(splitcmd[1])
      elif splitcmd[0] == "showfsconfig":
        if len(splitcmd) != 1:
          print ("Error: showfsconfig do not require argument")
        else:
          self.showfsconfig()
      elif splitcmd[0] == "load":
        if len(splitcmd) != 2:
          print ("Error: load requires 1 argument")
        else:
          self.load(splitcmd[1])
      elif splitcmd[0] == "save":
        if len(splitcmd) != 2:
          print ("Error: save requires 1 argument")
        else:
          self.save(splitcmd[1])
      elif splitcmd[0] == "exit":
        return
      else:
        print ("command " + splitcmd[0] + " not valid.\n")


if __name__ == "__main__":

  # Initialize file for logging
  # Change logging level to INFO to remove debugging messages
  logging.basicConfig(filename='memoryfs.log', filemode='w', level=logging.DEBUG)


  # Construct the argument parser
  ap = argparse.ArgumentParser()

  ap.add_argument('-nb', '--total_num_blocks', type=int, help='an integer value')
  ap.add_argument('-bs', '--block_size', type=int, help='an integer value')
  ap.add_argument('-ni', '--max_num_inodes', type=int, help='an integer value')
  ap.add_argument('-is', '--inode_size', type=int, help='an integer value')

  # Other than FS args, consecutive args will be captured in by 'arg' as list
  ap.add_argument('arg', nargs='*')

  args = ap.parse_args()

  # Initialize empty file system data
  logging.info('Initializing data structures...')
  RawBlocks = DiskBlocks(args)
  boot_block = b'\x12\x34\x56\x78' # constant 12345678 stored as beginning of boot block; no need to change this
  RawBlocks.InitializeBlocks(boot_block)


  # Print file system information and contents of first few blocks to memoryfs.log
  RawBlocks.PrintFSInfo()
  RawBlocks.PrintBlocks("Initialized",0,16)

  # Initialize FileObject inode
  FileObject = FileName(RawBlocks)

  # reload the global variables (in case they changed due to command line inputs)
  from memoryfs import *

  # Initalize root inode
  FileObject.InitRootInode()

  # Redirect INFO logs to console as well
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)
  logging.getLogger().addHandler(console_handler)

  # Run the interactive shell interpreter
  myshell = FSShell(FileObject)
  myshell.Interpreter()

