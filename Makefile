all: blog syntax-highlighting.css

clean:
	rm -f blog/*.html
	rm -f syntax-highlighting.css

blog: $(patsubst blog/%.md,blog/%.html,$(wildcard blog/*.md))

blog/%.html: blog/%.md blog-template.html Makefile
	pandoc --toc -s --css ../reset.css --css ../index.css --css ../syntax-highlighting.css --highlight-style tango -i $< -o $@ --template=blog-template.html \
		-V relative_path=..

syntax-highlighting.css:
	pandoc --print-highlight-style tango | python3 generate_css.py > $@

.PHONY: all clean blog
