# PrimeVue FloatLabel issue

In commit [355bbeb](https://github.com/primefaces/primevue/commit/355bbebe7e1cb8e1e42eaf76e06b10501d08f196) the old float label styles were removed from "components/lib/basecomponent/style/BaseComponentStyle.js" in favour of the new FloatLabel component with it's own component styles "components/lib/floatlabel/style/FloatLabelStyle.js". This takes affect in the PrimeVue update from v3.47.2 to v3.48.0.

(curiously, also some styles from input group were removed, though this is probably due to the mentioned Issue also containing some work regarding that and the removed classes loosely tie to float label)

Old CSS:
```css

/* Floating Label */
.p-float-label {
    display: block;
    position: relative;
}
.p-float-label label {
    position: absolute;
    pointer-events: none;
    top: 50%;
    margin-top: -.5rem;
    transition-property: all;
    transition-timing-function: ease;
    line-height: 1;
}
.p-float-label textarea ~ label {
    top: 1rem;
}
.p-float-label input:focus ~ label,
.p-float-label input.p-filled ~ label,
.p-float-label input:-webkit-autofill ~ label,
.p-float-label textarea:focus ~ label,
.p-float-label textarea.p-filled ~ label,
.p-float-label .p-inputwrapper-focus ~ label,
.p-float-label .p-inputwrapper-filled ~ label {
    top: -.75rem;
    font-size: 12px;
}
.p-float-label .p-placeholder,
.p-float-label input::placeholder,
.p-float-label .p-inputtext::placeholder {
    opacity: 0;
    transition-property: all;
    transition-timing-function: ease;
}
.p-float-label .p-focus .p-placeholder,
.p-float-label input:focus::placeholder,
.p-float-label .p-inputtext:focus::placeholder {
    opacity: 1;
    transition-property: all;
    transition-timing-function: ease;
}
```

New CSS:

```css
.p-float-label {
    display: block;
    position: relative;
}
.p-float-label label {
    position: absolute;
    pointer-events: none;
    top: 50%;
    margin-top: -.5rem;
    transition-property: all;
    transition-timing-function: ease;
    line-height: 1;
}
.p-float-label:has(textarea) label {
    top: 1rem;
}
.p-float-label:has(input:focus) label,
.p-float-label:has(input.p-filled) label,
.p-float-label:has(input:-webkit-autofill) label,
.p-float-label:has(textarea:focus) label,
.p-float-label:has(textarea.p-filled) label,
.p-float-label:has(.p-inputwrapper-focus) label,
.p-float-label:has(.p-inputwrapper-filled) label {
    top: -.75rem;
    font-size: 12px;
}
.p-float-label .p-placeholder,
.p-float-label input::placeholder,
.p-float-label .p-inputtext::placeholder {
    opacity: 0;
    transition-property: all;
    transition-timing-function: ease;
}
.p-float-label .p-focus .p-placeholder,
.p-float-label input:focus::placeholder,
.p-float-label .p-inputtext:focus::placeholder {
    opacity: 1;
    transition-property: all;
    transition-timing-function: ease;
}
```

The new version has been changed to use the :has() selector instead of the ~ sibling selector. The new version does not work on Firefox 115 ESR because firefox only supports :has() since 121 (which was only released at Dec 19 2023!). See https://www.mozilla.org/en-US/firefox/121.0/releasenotes/

To fix this, we can revert this back.

This was tested by finding the block

```css

.p-float-label:has(input:focus) label,
.p-float-label:has(input.p-filled) label,
.p-float-label:has(input:-webkit-autofill) label,
.p-float-label:has(textarea:focus) label,
.p-float-label:has(textarea.p-filled) label,
.p-float-label:has(.p-inputwrapper-focus) label,
.p-float-label:has(.p-inputwrapper-filled) label {
    top: -.75rem;
    font-size: 12px;
}

```

in the browser and replacing it again with the old version:

```css

.p-float-label input:focus ~ label,
.p-float-label input.p-filled ~ label,
.p-float-label input:-webkit-autofill ~ label,
.p-float-label textarea:focus ~ label,
.p-float-label textarea.p-filled ~ label,
.p-float-label .p-inputwrapper-focus ~ label,
.p-float-label .p-inputwrapper-filled ~ label {
    top: -.75rem;
    font-size: 12px;
}

```

After this temporary change, everything works fine, even in older versions of Firefox.

A better way to fix this would be to use a @supports selector instead, so that the newer version is used if available, since it otherwise will only work if the label element is placed after the input element.

This can be done by replacing the code with the following snippet:

```css

@supports selector(input:has(a)) {
    .p-float-label:has(input:focus) label,
    .p-float-label:has(input.p-filled) label,
    .p-float-label:has(input:-webkit-autofill) label,
    .p-float-label:has(textarea:focus) label,
    .p-float-label:has(textarea.p-filled) label,
    .p-float-label:has(.p-inputwrapper-focus) label,
    .p-float-label:has(.p-inputwrapper-filled) label {
      top: -0.75rem;
      font-size: 12px;
    }
  }
  @supports not selector(input:has(a)) {
    .p-float-label input:focus ~ label,
    .p-float-label input.p-filled ~ label,
    .p-float-label input:-webkit-autofill ~ label,
    .p-float-label textarea:focus ~ label,
    .p-float-label textarea.p-filled ~ label,
    .p-float-label .p-inputwrapper-focus ~ label,
    .p-float-label .p-inputwrapper-filled ~ label {
      top: -.75rem;
      font-size: 12px;
    }
  }

```

To test this more semi-permanently in a project, find the compiled theme.css file for the theme you are using (not sure how this works in unstyled mode) and then perform this replacement there. This will survive reloads.

The permanent fix (possible PR submission) would be to replace this in the repository file "components/lib/floatlabel/style/FloatLabelStyle.js" along with any other use of the :has() selector in there.

Also: update to Firefox non-esr on Debian, which is now possible in a clean way: https://linuxiac.com/how-to-install-the-latest-firefox-on-debian-12/

