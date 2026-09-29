source "https://rubygems.org"

# Keep the Pages-compatible renderer without the github-pages umbrella gem.
# Its unused remote-theme dependency pins vulnerable rubyzip < 3.0.
gem "jekyll", "= 3.10.0"
gem "kramdown", "= 2.4.0"
gem "kramdown-parser-gfm", "= 1.1.0"
gem "rouge", "= 3.30.0"

# GHSA-9hj4-r449-hfvc: fixed in JSON 2.21.2.
gem "json", ">= 2.21.2", "< 3"
gem "wdm", "~> 0.1.0" if Gem.win_platform?

group :jekyll_plugins do
  gem "jekyll-paginate", "= 1.1.0"
  gem "jekyll-sitemap", "= 1.4.0"
  gem "jekyll-gist", "= 1.5.0"
  gem "jekyll-feed", "= 0.17.0"
  gem "jekyll-redirect-from", "= 0.16.0"
  gem "hawkins", "= 2.0.5"
end
