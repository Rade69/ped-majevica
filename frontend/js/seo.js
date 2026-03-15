/**
 * SEO Utilities - Structured Data (Schema.org) for PED Majevica
 * Adds JSON-LD structured data for better SEO
 */

const SEO = (function () {
  "use strict";

  // Organization schema
  const organizationSchema = {
    "@context": "https://schema.org",
    "@type": "SportsClub",
    name: "PED Majevica 1988",
    description:
      "Planinarsko društvo Majevica 1988 - Uživajte u prelepim planinama i avanturama",
    url: "https://pedmajevica.org",
    logo: "https://pedmajevica.org/images/logo.png",
    image: "https://pedmajevica.org/images/hero/hero-mountains.png",
    telephone: "+387 65 581 354",
    email: "info@pedmajevica.org",
    address: {
      "@type": "PostalAddress",
      addressLocality: "Majevica",
      addressCountry: "BA",
    },
    sameAs: [
      "https://www.facebook.com/pedmajevica",
      "https://www.instagram.com/pedmajevica",
      "https://www.youtube.com/channel/UCxxx",
    ],
    foundingDate: "1988",
    keywords: "planinarenje, hiking, Majevica, outdoor, avantura",
  };

  // Navigation menu schema
  const navigationSchema = {
    "@context": "https://schema.org",
    "@type": "SiteNavigationElement",
    name: ["Početna", "Galerija", "Članstvo", "Prijavi se"],
    url: [
      "https://pedmajevica.org/",
      "https://pedmajevica.org/galerija.html",
      "https://pedmajevica.org/uclanite-se.html",
      "https://pedmajevica.org/login.html",
    ],
  };

  /**
   * Add organization structured data
   */
  function addOrganizationSchema() {
    addJSONLD(organizationSchema);
  }

  /**
   * Add blog post structured data
   * @param {object} post - Post object with title, content, date, image
   */
  function addBlogPostSchema(post) {
    const schema = {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      headline: post.title,
      description: post.preview || post.content.substring(0, 160),
      image: post.image || "https://pedmajevica.org/images/blog/default.jpg",
      datePublished: post.created_at,
      dateModified: post.updated_at || post.created_at,
      author: {
        "@type": "Organization",
        name: "PED Majevica 1988",
        url: "https://pedmajevica.org",
      },
      publisher: {
        "@type": "Organization",
        name: "PED Majevica 1988",
        logo: {
          "@type": "ImageObject",
          url: "https://pedmajevica.org/images/logo.png",
        },
      },
      mainEntityOfPage: {
        "@type": "WebPage",
        "@id": `https://pedmajevica.org/blog/${post.slug}`,
      },
      keywords: post.category || "planinarenje",
    };

    addJSONLD(schema);
  }

  /**
   * Add event structured data
   * @param {object} event - Event object
   */
  function addEventSchema(event) {
    const schema = {
      "@context": "https://schema.org",
      "@type": "Event",
      name: event.title,
      description: event.description,
      startDate: event.event_date,
      endDate: event.event_date,
      eventStatus: "https://schema.org/EventScheduled",
      eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode",
      location: {
        "@type": "Place",
        name: event.location || "Majevica",
        address: {
          "@type": "PostalAddress",
          addressLocality: "Majevica",
          addressCountry: "BA",
        },
      },
      image: event.image || "https://pedmajevica.org/images/events/default.jpg",
      organizer: {
        "@type": "Organization",
        name: "PED Majevica 1988",
        url: "https://pedmajevica.org",
      },
    };

    if (event.max_participants) {
      schema.maximumAttendeeCapacity = event.max_participants;
    }

    addJSONLD(schema);
  }

  /**
   * Add hiking trail structured data
   * @param {object} trail - Trail object
   */
  function addTrailSchema(trail) {
    const schema = {
      "@context": "https://schema.org",
      "@type": "TouristAttraction",
      name: trail.name,
      description: trail.description,
      image: trail.images?.[0] || "https://pedmajevica.org/images/trails/default.jpg",
      address: {
        "@type": "PostalAddress",
        addressLocality: trail.region || "Majevica",
        addressCountry: "BA",
      },
      additionalProperty: [
        {
          "@type": "PropertyValue",
          name: "Difficulty",
          value: trail.difficulty,
        },
        {
          "@type": "PropertyValue",
          name: "Distance",
          value: `${trail.distance_km} km`,
        },
        {
          "@type": "PropertyValue",
          name: "Duration",
          value: `${trail.duration_hours} hours`,
        },
        {
          "@type": "PropertyValue",
          name: "Elevation Gain",
          value: `${trail.elevation_gain_m} m`,
        },
      ],
    };

    addJSONLD(schema);
  }

  /**
   * Add FAQ structured data
   * @param {Array} faqs - Array of FAQ objects {question, answer}
   */
  function addFAQSchema(faqs) {
    const schema = {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      mainEntity: faqs.map((faq) => ({
        "@type": "Question",
        name: faq.question,
        acceptedAnswer: {
          "@type": "Answer",
          text: faq.answer,
        },
      })),
    };

    addJSONLD(schema);
  }

  /**
   * Add breadcrumb structured data
   * @param {Array} items - Array of breadcrumb items {name, url}
   */
  function addBreadcrumbSchema(items) {
    const schema = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: items.map((item, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: item.name,
        item: item.url,
      })),
    };

    addJSONLD(schema);
  }

  /**
   * Add WebSite schema with search action
   */
  function addWebsiteSchema() {
    const schema = {
      "@context": "https://schema.org",
      "@type": "WebSite",
      name: "PED Majevica 1988",
      url: "https://pedmajevica.org",
      potentialAction: {
        "@type": "SearchAction",
        target: {
          "@type": "EntryPoint",
          urlTemplate: "https://pedmajevica.org/search?q={search_term_string}",
        },
        "query-input": "required name=search_term_string",
      },
    };

    addJSONLD(schema);
  }

  /**
   * Add JSON-LD script to head
   * @param {object} schema - Schema object
   */
  function addJSONLD(schema) {
    // Remove existing script with same @type
    const existingScript = document.querySelector(
      `script[type="application/ld+json"][data-seo="${schema["@type"]}"]`
    );
    if (existingScript) {
      existingScript.remove();
    }

    // Create new script
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.setAttribute("data-seo", schema["@type"]);
    script.textContent = JSON.stringify(schema);

    // Add to head
    document.head.appendChild(script);

    console.log(`✅ Added SEO schema: ${schema["@type"]}`);
  }

  /**
   * Add meta tags for Open Graph and Twitter
   * @param {object} options - Meta tag options
   */
  function addMetaTags(options = {}) {
    const {
      title = "PED Majevica 1988",
      description = "Planinarsko društvo Majevica 1988 - Uživajte u prelepim planinama i avanturama",
      image = "https://pedmajevica.org/images/hero/hero-mountains.png",
      url = window.location.href,
      type = "website",
    } = options;

    // Open Graph
    setMetaTag("og:title", title);
    setMetaTag("og:description", description);
    setMetaTag("og:image", image);
    setMetaTag("og:url", url);
    setMetaTag("og:type", type);
    setMetaTag("og:site_name", "PED Majevica 1988");

    // Twitter Card
    setMetaTag("twitter:card", "summary_large_image");
    setMetaTag("twitter:title", title);
    setMetaTag("twitter:description", description);
    setMetaTag("twitter:image", image);

    // Additional
    setMetaTag("description", description);
  }

  /**
   * Set meta tag
   * @param {string} name - Meta tag name
   * @param {string} content - Meta tag content
   */
  function setMetaTag(name, content) {
    let meta = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);

    if (!meta) {
      meta = document.createElement("meta");
      if (name.startsWith("og:") || name.startsWith("twitter:")) {
        meta.setAttribute("property", name);
      } else {
        meta.setAttribute("name", name);
      }
      document.head.appendChild(meta);
    }

    meta.setAttribute("content", content);
  }

  /**
   * Initialize SEO for current page
   */
  function init() {
    // Add website schema on all pages
    addWebsiteSchema();

    // Add organization schema on all pages
    addOrganizationSchema();

    // Add default meta tags
    addMetaTags();

    console.log("✅ SEO initialized");
  }

  // Public API
  return {
    init,
    addOrganizationSchema,
    addBlogPostSchema,
    addEventSchema,
    addTrailSchema,
    addFAQSchema,
    addBreadcrumbSchema,
    addWebsiteSchema,
    addJSONLD,
    addMetaTags,
  };
})();

// Auto-initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", SEO.init);
} else {
  SEO.init();
}

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = SEO;
}
