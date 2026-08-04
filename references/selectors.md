# CandyMapper contact form — full selector map

Collected live 2026-08-04 via `vibium eval` enumerating every `input`/`textarea`/
`select`/`button` on the page after dismissing the Pop-Up Challenge modal. Previously only
two of these (First Name, Email) were used anywhere in this repo, in `scripts/config.sh`.
This is the full set, for reuse in any future test run against this form.

| field | selector | required? | notes |
|---|---|---|---|
| First Name | `input[data-aid="First Name"]` | yes | used in `config.sh` |
| Last Name | `input[data-aid="Last Name"]` | no | |
| Email | `input[data-aid="CONTACT_FORM_EMAIL"]` | yes | used in `config.sh` |
| Phone | `input[data-aid="By entering a Phone Number you agree to our SMS Terms of Service"]` | no | **quirk**: the `data-aid` value is the SMS disclaimer text, not a field name |
| Message | `textarea[data-aid="CONTACT_FORM_MESSAGE"]` | no | |
| Submit | `button[data-aid="CONTACT_SUBMIT_BUTTON_REND"]` | — | used everywhere |

Only First Name and Email are actually enforced by validation — confirmed both by the
article's own findings and by this map (the other three accept empty submission).

## Why `data-aid`, never `id`

Every element above also has a generated `id` (`input14`, `input15`, `input16`,
`input17`) that changes on rebuild — see `methodology.md`'s locator section. `data-aid`
is stable across rebuilds; the `id`s are not. Never key a locator on these `input`
elements' `id`.

## "Contact Us" scroll target

The section heading itself (`<h2>Contact Us</h2>`) has **no `id` and no `data-aid`** —
only generated utility classes (`x-el x-el-h2 c1-1 c1-2 ...`), the same kind of unstable
identifier this file's own locator rule warns against. Don't select the heading directly.
Scroll `input[data-aid="First Name"]` into view instead — same practical destination
("scroll down to Contact Us"), on a selector already proven stable.

## Noise on the page — not part of the contact form

- A hidden `_app_id` input (name attribute, no `data-aid`).
- A cluster of `goog-gt-*`-prefixed fields (`goog-gt-thumbUpButton`,
  `goog-gt-votingInputSrcLang`, etc.) — belongs to a Google Translate widget injected on
  the page, unrelated to the form.
- A `g-recaptcha-response-100000` textarea — reCAPTCHA's own hidden field.

## How this was collected

```js
Array.from(document.querySelectorAll('input, textarea, select, button')).map(el => ({
  tag: el.tagName.toLowerCase(), type: el.type || '',
  dataAid: el.getAttribute('data-aid') || '', id: el.id || '',
  name: el.name || '', placeholder: el.placeholder || '', required: el.required || false
})).filter(x => x.dataAid || x.id || x.name)
```

Run via `vibium eval "<above, one line>"` after navigating to the page and dismissing the
modal. Re-run this if the form is ever suspected to have changed — this file is a
snapshot, not a live source.
