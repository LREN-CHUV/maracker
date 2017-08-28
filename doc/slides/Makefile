SOURCES = slides.md
SLIDES = slides.html
PDFS = slides.pdf

.PHONY: all
all: html pdf

.PHONY: html
html: $(SLIDES)

.PHONY: pdf
pdf: $(PDFS)

.PHONY: install
install:
	git clone https://github.com/hakimel/reveal.js.git

$(SLIDES): %.html: %.md
	pandoc -s -S -t revealjs slides.md -o slides.html \
		--css https://fonts.googleapis.com/icon?family=Material+Icons \
		-H theme.html \
		--self-contained \
		--variable theme="beige" \
		--variable transition="slide" \

$(PDFS): %.pdf: %.md
	pandoc --latex-engine=xelatex \
		-f markdown \
		-t latex \
		-H theme.tex \
		--variable papersize=a4 \
		--variable fontsize=12pt \
		--variable mainfont="Linux Libertine O" \
		--variable sansfont="Linux Biolinum O" \
		--variable monofont="Inconsolata" \
		--variable monofontoptions="Scale=0.9" \
		--variable linkcolor="blue" \
		--variable urlcolor="blue" \
		-o $@ \
		$^

.PHONY: clean
clean:
	rm -f $(PDFS) $(SLIDES)
