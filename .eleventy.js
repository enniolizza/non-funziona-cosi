module.exports = function (eleventyConfig) {
    eleventyConfig.setNunjucksEnvironmentOptions({
        lstripBlocks: true,
        trimBlocks: true
    });

    eleventyConfig.addPassthroughCopy({
        'src/assets': 'assets',
        'src/articoli/petrolio_wti/images': 'articoli/petrolio_wti/images',
        'src/articoli/superbonus_110/images': 'articoli/superbonus_110/images',
        'src/robots.txt': 'robots.txt',
        'src/sitemap.xml': 'sitemap.xml',
        'src/.nojekyll': '.nojekyll'
    });

    return {
        dir: {
            input: 'src',
            includes: '_includes',
            output: '_site'
        },
        templateFormats: ['njk'],
        htmlTemplateEngine: 'njk',
        markdownTemplateEngine: 'njk',
        dataTemplateEngine: 'njk'
    };
};
