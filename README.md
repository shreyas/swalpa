
# About Swalpa

    `'Swalpa' (स्वल्प in संस्क्रुत) means small/short.`

This was 2-3 years back. I wanted to build a blogging website (for my own use). Twitter's bootstrap was something that had wowed me with its simplicity. But hand-coding any HTML disgusts me. 'Angular bracket languages are for machines not humans', I would tell myself before widing things down even before they began. 

If only there were something that would let me lazily write HTML at the speed of thought... If only there was some short-hand that could be parsed into full-blown HTML... Well, that's how Swalpa was concieved. 

This is an example snippet that I had in mind, for creating a navbar using bootstrap - 

```
navbar {
    header {
        branding ["http://the.link.com/"] { 
            "Site\"Builder\"Mde"; 
            img [images/brand.png] 
        }
        toggle (pull-left) [navbar-example1-collapse] { }
        toggle (pull-right) [navbar-example2-collapse] { }
    }
    menu (navbar-example1-collapse) {
        link(#placeholder classes)[http://the.link.com/] { 
            "Placeholder"; 
            img [http://placehold.it/75x15] 
        }
        divider;
        link(#somelink classes) [http://the.link.com/somelink] {"Some Link"}
        divider;
        form (navbar-left) [role: "search"] [type: form] {
            textbox(#id form-control) [placeholder: "Search String"];
            submit_button {"Submit"}
        }
    }
    menu (navbar-right navbar-example2-collapse) ["File"] {
        branding ["http://the.link.com/"] { "Illplaced Branding" }
        link(#file.new classes) [file/new] { "New"}
        link(#file.open classes) [file/open] { "Open"}      
        link(#file.save some content antherclass) [file/save] { "Save"}
    }
    menuitem [http://some.link.com] { "SomeLink" } 
}
```

Swalpa was my attempt at writing such a parser that would parse these shorthand notations and blow them back into navbar HTML, which bootstrap understands. 

But... and there comes the but. It was pretty nieve of me to use 'regular'-expressions as basic building blocks for parsing shorthand to a context free language like HTML. Sooner or later, pumping-lemma would bite me ... and bite it did. I knew I had hit the wall. Pumping lemma was a revealation. Swalpa was a pretty ambitious, though nieve, approach at parsing text, without knowing the underlying language theory. 

.... and then I found out about [Emmet](http://emmet.io/). The whole purpose of writing this parser was gone. 

I wound down Swalpa, and it remained in the closet, like many other things, till I had some motivation and time to take efforts and put it on a public repo. 

A fun fact in the code. I was a c++/oop fan. With OOP/OOAD, I stil remain a fan; c++ not so much so. So I wrote a lot of code to 'emulate' guaranteed overrides and virtuals ala c++ in python. I hadn't discovered ABCs in python back then, and the thought process that's needed to map the design patterns from static to dynamic world had not yet begun. 


# What's In

All the source code. All of it (there isn't much, to be honest). As is. No guarantees. 
In fact, if your system goes in flame because you ran Swalpa on it, I will be the one sueing you for using Swalpa for violence. 


# Current Status 

Wound down. Dead. In the museum. Amusement park. In extract-the-good-parts-before-you-throw-it-in-the-bin state.
