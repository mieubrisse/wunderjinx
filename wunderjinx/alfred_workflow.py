import sys
import wunderjinx

# Because we don't want to deal with quoting and escaping in Alfred, we'll pass all of the Alfred params as a single string and let the spliting happen here instead of at the Bash level
if len(sys.argv) != 2:
    sys.stderr.write("Error: No arguments passed\n")
    sys.exit(1)
# We don't have to use a filer(None, ) here because split() without a separator automatically removes empty strings
args = sys.argv[1].split()
wunderjinx.main(argv=args)

